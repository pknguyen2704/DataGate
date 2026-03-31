import argparse
import io
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import psycopg2
from dotenv import load_dotenv
from psycopg2 import sql
from pyarrow.parquet import ParquetFile


DEFAULT_PATTERN = "*.parquet"
DEFAULT_WORKERS = 4
DEFAULT_CHUNK_ROWS = 200_000
DEFAULT_TABLE_PREFIX = "tlc_data_"
DEFAULT_NULL_TOKEN = r"\N"


@dataclass(frozen=True)
class UploadTask:
    file_path: Path
    table_name: str
    replace_table: bool


@dataclass(frozen=True)
class UploadResult:
    file_name: str
    table_name: str
    rows_uploaded: int
    elapsed_seconds: float
    status: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Upload parquet files to PostgreSQL using COPY."
    )
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument("--data-dir", help="Directory containing parquet files.")
    source_group.add_argument(
        "--file",
        dest="files",
        action="append",
        help="Parquet file to upload. Repeat for multiple files.",
    )

    parser.add_argument("--pattern", default=DEFAULT_PATTERN)
    parser.add_argument("--db-url", default=build_default_db_url())
    parser.add_argument("--table", help="Target table for all files.")
    parser.add_argument("--table-prefix", default=DEFAULT_TABLE_PREFIX)
    parser.add_argument("--mode", choices=["append", "replace"], default="append")
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    parser.add_argument("--chunk-rows", type=int, default=DEFAULT_CHUNK_ROWS)
    parser.add_argument("--csv-null", default=DEFAULT_NULL_TOKEN)
    parser.add_argument(
        "--date-hour",
        help="Filter rows to a specific hour. Format: YYYY-MM-DD HH:00:00",
    )
    parser.add_argument("--no-verbose", action="store_true")
    return parser.parse_args()


def build_default_db_url() -> str:
    env_file = Path(__file__).resolve().parent.parent / "data_source" / "postgres" / ".env"
    load_dotenv(env_file)

    user = os.getenv("POSTGRES_USER", "admin")
    password = os.getenv("POSTGRES_PASSWORD", "postgrespassword")
    database = os.getenv("POSTGRES_DB", "postgres")
    host = os.getenv("POSTGRES_HOST", "127.0.0.1")
    port = os.getenv("POSTGRES_PORT", "54321")
    return f"postgresql://{user}:{password}@{host}:{port}/{database}"


def collect_file_paths(args: argparse.Namespace) -> list[Path]:
    if args.data_dir:
        data_dir = Path(args.data_dir).resolve()
        if not data_dir.exists():
            raise FileNotFoundError(f"Directory does not exist: {data_dir}")

        file_paths = sorted(data_dir.glob(args.pattern))
        if not file_paths:
            raise FileNotFoundError(
                f"No files matching '{args.pattern}' were found in {data_dir}"
            )
        return file_paths

    file_paths: list[Path] = []
    for raw_path in args.files or []:
        file_path = Path(raw_path).resolve()
        if not file_path.exists():
            raise FileNotFoundError(f"File does not exist: {file_path}")
        file_paths.append(file_path)
    return file_paths


def build_upload_tasks(file_paths: list[Path], args: argparse.Namespace) -> list[UploadTask]:
    tasks: list[UploadTask] = []
    for index, file_path in enumerate(file_paths):
        table_name = args.table or derive_table_name(file_path, args.table_prefix)
        replace_table = args.mode == "replace" and (args.table is None or index == 0)
        tasks.append(
            UploadTask(
                file_path=file_path,
                table_name=table_name,
                replace_table=replace_table,
            )
        )
    return tasks


def derive_table_name(file_path: Path, table_prefix: str) -> str:
    return sanitize_identifier(f"{table_prefix}{file_path.stem}")


def sanitize_identifier(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_]+", "_", value.strip().lower())
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    if not cleaned:
        raise ValueError(f"Could not derive a valid SQL identifier from: {value!r}")
    if cleaned[0].isdigit():
        cleaned = f"t_{cleaned}"
    return cleaned


def normalize_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    renamed_columns = [sanitize_identifier(str(column)) for column in dataframe.columns]
    renamed_dataframe = dataframe.copy()
    renamed_dataframe.columns = renamed_columns
    return renamed_dataframe


def parse_target_hour(raw_value: str | None) -> pd.Timestamp | None:
    if not raw_value:
        return None

    timestamp = pd.Timestamp(raw_value)
    if pd.isna(timestamp):
        raise ValueError(f"Invalid --date-hour value: {raw_value}")
    return timestamp.floor("h")


def detect_datetime_column(columns: list[str]) -> str | None:
    preferred_columns = [
        column for column in columns if "pickup" in column and "datetime" in column
    ]
    if preferred_columns:
        return preferred_columns[0]

    matching_columns = [column for column in columns if "datetime" in column]
    return matching_columns[0] if matching_columns else None


def filter_dataframe_by_hour(
    dataframe: pd.DataFrame,
    target_hour: pd.Timestamp | None,
) -> pd.DataFrame:
    if target_hour is None or dataframe.empty:
        return dataframe

    datetime_column = detect_datetime_column(list(dataframe.columns))
    if datetime_column is None:
        return dataframe

    filtered_dataframe = dataframe.copy()
    filtered_dataframe[datetime_column] = pd.to_datetime(
        filtered_dataframe[datetime_column], errors="coerce"
    )
    return filtered_dataframe[
        filtered_dataframe[datetime_column].dt.floor("h") == target_hour
    ]


def iter_parquet_chunks(file_path: Path, chunk_rows: int):
    parquet_file = ParquetFile(file_path)
    for batch in parquet_file.iter_batches(batch_size=chunk_rows):
        dataframe = normalize_columns(batch.to_pandas())
        yield dataframe


def align_dataframe_columns(
    dataframe: pd.DataFrame, expected_columns: list[str]
) -> pd.DataFrame:
    missing_columns = [column for column in expected_columns if column not in dataframe.columns]
    unexpected_columns = [column for column in dataframe.columns if column not in expected_columns]

    if missing_columns or unexpected_columns:
        raise ValueError(
            "Column mismatch. "
            f"Missing columns: {missing_columns or 'none'}. "
            f"Unexpected columns: {unexpected_columns or 'none'}."
        )

    return dataframe[expected_columns]


def infer_postgres_type(series: pd.Series) -> sql.SQL:
    if pd.api.types.is_bool_dtype(series):
        return sql.SQL("BOOLEAN")
    if pd.api.types.is_integer_dtype(series):
        return sql.SQL("BIGINT")
    if pd.api.types.is_float_dtype(series):
        return sql.SQL("DOUBLE PRECISION")
    if pd.api.types.is_datetime64_any_dtype(series):
        return sql.SQL("TIMESTAMP")
    if pd.api.types.is_date_dtype(series):
        return sql.SQL("DATE")
    return sql.SQL("TEXT")


def create_table(
    connection,
    table_name: str,
    sample_dataframe: pd.DataFrame,
    replace_table: bool,
) -> None:
    column_definitions = []
    for column_name, dtype in sample_dataframe.dtypes.items():
        series = pd.Series(dtype=dtype)
        column_definitions.append(
            sql.SQL("{} {}").format(
                sql.Identifier(column_name),
                infer_postgres_type(series),
            )
        )

    with connection.cursor() as cursor:
        if replace_table:
            cursor.execute(
                sql.SQL("DROP TABLE IF EXISTS {}").format(sql.Identifier(table_name))
            )
        cursor.execute(
            sql.SQL("CREATE TABLE IF NOT EXISTS {} ({})").format(
                sql.Identifier(table_name),
                sql.SQL(", ").join(column_definitions),
            )
        )
    connection.commit()


def copy_dataframe_to_postgres(
    connection,
    table_name: str,
    dataframe: pd.DataFrame,
    csv_null: str,
) -> None:
    buffer = io.StringIO()
    dataframe.to_csv(
        buffer,
        index=False,
        header=False,
        sep=",",
        na_rep=csv_null,
        lineterminator="\n",
    )
    buffer.seek(0)

    copy_statement = sql.SQL(
        "COPY {} ({}) FROM STDIN WITH (FORMAT CSV, DELIMITER ',', NULL {})"
    ).format(
        sql.Identifier(table_name),
        sql.SQL(", ").join(sql.Identifier(column) for column in dataframe.columns),
        sql.Literal(csv_null),
    )

    with connection.cursor() as cursor:
        cursor.copy_expert(copy_statement.as_string(connection), buffer)
    connection.commit()


def test_database_connection(db_url: str) -> None:
    with psycopg2.connect(db_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")


def load_first_non_empty_chunk(
    file_paths: list[Path],
    chunk_rows: int,
    target_hour: pd.Timestamp | None,
) -> pd.DataFrame | None:
    for file_path in file_paths:
        for chunk in iter_parquet_chunks(file_path, chunk_rows):
            filtered_chunk = filter_dataframe_by_hour(chunk, target_hour)
            if not filtered_chunk.empty:
                return filtered_chunk
    return None


def upload_file(
    task: UploadTask,
    db_url: str,
    chunk_rows: int,
    csv_null: str,
    target_hour: pd.Timestamp | None,
    verbose: bool,
    expected_columns: list[str] | None = None,
) -> UploadResult:
    started_at = time.time()
    rows_uploaded = 0
    table_initialized = False

    try:
        with psycopg2.connect(db_url) as connection:
            for chunk_index, chunk in enumerate(iter_parquet_chunks(task.file_path, chunk_rows), start=1):
                filtered_chunk = filter_dataframe_by_hour(chunk, target_hour)
                if filtered_chunk.empty:
                    continue

                if expected_columns is not None:
                    filtered_chunk = align_dataframe_columns(filtered_chunk, expected_columns)

                if not table_initialized:
                    create_table(
                        connection=connection,
                        table_name=task.table_name,
                        sample_dataframe=filtered_chunk.head(100),
                        replace_table=task.replace_table,
                    )
                    table_initialized = True
                    if verbose:
                        print(f"[{task.file_path.name}] Table {task.table_name} is ready.")

                copy_dataframe_to_postgres(
                    connection=connection,
                    table_name=task.table_name,
                    dataframe=filtered_chunk,
                    csv_null=csv_null,
                )
                rows_uploaded += len(filtered_chunk)

                if verbose:
                    print(
                        f"[{task.file_path.name}] Uploaded chunk {chunk_index} "
                        f"({len(filtered_chunk)} rows, total={rows_uploaded})."
                    )

        if rows_uploaded == 0:
            return UploadResult(
                file_name=task.file_path.name,
                table_name=task.table_name,
                rows_uploaded=0,
                elapsed_seconds=time.time() - started_at,
                status="EMPTY",
            )

        return UploadResult(
            file_name=task.file_path.name,
            table_name=task.table_name,
            rows_uploaded=rows_uploaded,
            elapsed_seconds=time.time() - started_at,
            status="OK",
        )
    except Exception as exc:
        return UploadResult(
            file_name=task.file_path.name,
            table_name=task.table_name,
            rows_uploaded=rows_uploaded,
            elapsed_seconds=time.time() - started_at,
            status=f"ERR: {exc}",
        )


def upload_many_files(
    tasks: list[UploadTask],
    db_url: str,
    chunk_rows: int,
    csv_null: str,
    target_hour: pd.Timestamp | None,
    workers: int,
    verbose: bool,
    expected_columns: list[str] | None = None,
) -> list[UploadResult]:
    results: list[UploadResult] = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(
                upload_file,
                task,
                db_url,
                chunk_rows,
                csv_null,
                target_hour,
                verbose,
                expected_columns,
            )
            for task in tasks
        ]
        for future in as_completed(futures):
            results.append(future.result())
    return results


def print_summary(results: list[UploadResult], total_elapsed_seconds: float) -> None:
    successful_results = [result for result in results if result.status == "OK"]
    total_rows = sum(result.rows_uploaded for result in successful_results)

    print("\n=== Summary ===")
    for result in sorted(results, key=lambda item: item.file_name):
        print(
            f"{result.status:>10}  "
            f"{result.file_name:40} -> "
            f"{result.table_name:30}  "
            f"rows={result.rows_uploaded:<10}  "
            f"time={result.elapsed_seconds:6.2f}s"
        )

    print(f"\nTotal uploaded rows: {total_rows}")
    print(f"Total execution time: {total_elapsed_seconds:.2f} seconds")
    if total_elapsed_seconds > 0:
        print(f"Approx throughput: {total_rows / total_elapsed_seconds:,.0f} rows/sec")


def main() -> None:
    args = parse_args()
    verbose = not args.no_verbose
    target_hour = parse_target_hour(args.date_hour)
    file_paths = collect_file_paths(args)
    tasks = build_upload_tasks(file_paths, args)

    if verbose:
        print(f"Discovered {len(file_paths)} parquet file(s).")
        print("Checking database connection...")
    test_database_connection(args.db_url)

    total_started_at = time.time()

    if args.table:
        sample_chunk = load_first_non_empty_chunk(file_paths, args.chunk_rows, target_hour)
        expected_columns = list(sample_chunk.columns) if sample_chunk is not None else None

        if sample_chunk is not None:
            with psycopg2.connect(args.db_url) as connection:
                create_table(
                    connection=connection,
                    table_name=sanitize_identifier(args.table),
                    sample_dataframe=sample_chunk.head(100),
                    replace_table=args.mode == "replace",
                )
            tasks = [
                UploadTask(
                    file_path=task.file_path,
                    table_name=sanitize_identifier(args.table),
                    replace_table=False,
                )
                for task in tasks
            ]

        if args.workers > 2 and verbose:
            print(
                "Using a shared target table. "
                "If write contention is high, try --workers 1 or --workers 2."
            )

        results = upload_many_files(
            tasks=tasks,
            db_url=args.db_url,
            chunk_rows=args.chunk_rows,
            csv_null=args.csv_null,
            target_hour=target_hour,
            workers=args.workers,
            verbose=verbose,
            expected_columns=expected_columns,
        )
    else:
        results = upload_many_files(
            tasks=tasks,
            db_url=args.db_url,
            chunk_rows=args.chunk_rows,
            csv_null=args.csv_null,
            target_hour=target_hour,
            workers=args.workers,
            verbose=verbose,
        )

    print_summary(results, time.time() - total_started_at)


if __name__ == "__main__":
    main()
