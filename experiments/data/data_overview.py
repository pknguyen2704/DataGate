import argparse
from pathlib import Path
from typing import Iterable, List, Optional

import pandas as pd
import pyarrow.parquet as pq


DEFAULT_DATA_ROOT = Path(__file__).resolve().parent / "parquets"
DEFAULT_OUT_DIR = Path(__file__).resolve().parent / "overview"
DEFAULT_PREVIEW_ROWS = 10
TOP_VALUE_CARDINALITY_LIMIT = 15
HIGH_CARDINALITY_RATIO = 0.90
TIME_BUCKETS = ("day", "month", "hour")


def discover_parquet_files(paths: Iterable[Path]) -> List[Path]:
    files: List[Path] = []
    for path in paths:
        if path.is_dir():
            files.extend(sorted(path.rglob("*.parquet")))
        elif path.is_file() and path.suffix == ".parquet":
            files.append(path)
        else:
            raise FileNotFoundError(f"No parquet file or directory found at: {path}")
    return sorted(dict.fromkeys(files))


def load_data(parquet_file: pq.ParquetFile, row_limit: Optional[int]) -> pd.DataFrame:
    if row_limit is None:
        return parquet_file.read().to_pandas()

    batches = parquet_file.iter_batches(batch_size=row_limit)
    try:
        batch = next(batches)
    except StopIteration:
        return pd.DataFrame()
    return batch.to_pandas()


def parquet_schema_table(parquet_file: pq.ParquetFile) -> pd.DataFrame:
    rows = []
    for field in parquet_file.schema_arrow:
        rows.append(
            {
                "column": field.name,
                "parquet_type": str(field.type),
                "nullable": field.nullable,
            }
        )
    return pd.DataFrame(rows)


def dtype_label(series: pd.Series) -> str:
    if pd.api.types.is_object_dtype(series) or pd.api.types.is_string_dtype(series):
        return "str"
    return str(series.dtype)


def column_health_table(data: pd.DataFrame) -> pd.DataFrame:
    row_count = len(data)
    rows = []
    for column in data.columns:
        series = data[column]
        null_count = int(series.isna().sum())
        non_null = int(row_count - null_count)
        rows.append(
            {
                "column": column,
                "dtype": dtype_label(series),
                "non_null": non_null,
                "null": null_count,
                "null_%": round((null_count / row_count) * 100, 4) if row_count else 0.0,
                "unique": int(series.nunique(dropna=True)),
            }
        )
    return pd.DataFrame(rows)


def numeric_statistics_table(data: pd.DataFrame) -> pd.DataFrame:
    rows = []
    numeric = data.select_dtypes(include=["number"])
    for column in numeric.columns:
        series = numeric[column].dropna()
        if series.empty:
            continue
        rows.append(
            {
                "column": column,
                "min": series.min(),
                "p25": series.quantile(0.25),
                "median": series.median(),
                "mean": series.mean(),
                "p75": series.quantile(0.75),
                "max": series.max(),
                "std": series.std(),
            }
        )
    return pd.DataFrame(rows)


def datetime_coverage_table(data: pd.DataFrame) -> pd.DataFrame:
    rows = []
    datetimes = data.select_dtypes(include=["datetime", "datetimetz"])
    for column in datetimes.columns:
        series = datetimes[column].dropna()
        if series.empty:
            continue
        min_ts = series.min()
        max_ts = series.max()
        rows.append(
            {
                "column": column,
                "min_ts": min_ts,
                "max_ts": max_ts,
                "span": max_ts - min_ts,
            }
        )
    return pd.DataFrame(rows)


def bucket_datetime(series: pd.Series, bucket: str) -> pd.Series:
    if bucket == "hour":
        return series.dt.floor("h").astype(str)
    if bucket == "month":
        return series.dt.to_period("M").astype(str)
    return series.dt.floor("D").dt.date.astype(str)


def datetime_distribution_table(data: pd.DataFrame, bucket: str) -> pd.DataFrame:
    rows = []
    datetimes = data.select_dtypes(include=["datetime", "datetimetz"])
    for column in datetimes.columns:
        series = data[column].dropna()
        if series.empty:
            continue

        counts = bucket_datetime(series, bucket).value_counts().sort_index()
        total = int(counts.sum())
        for time_bucket, count in counts.items():
            rows.append(
                {
                    "column": column,
                    bucket: time_bucket,
                    "rows": int(count),
                    "row_%": round((int(count) / total) * 100, 4) if total else 0.0,
                }
            )
    return pd.DataFrame(rows)


def format_top_value(value: object) -> str:
    if pd.isna(value):
        return "<NULL>"
    return str(value)


def top_values_table(data: pd.DataFrame, health: pd.DataFrame, top_n: int) -> pd.DataFrame:
    rows = []
    unique_by_column = dict(zip(health["column"], health["unique"]))
    for column in data.columns:
        unique_count = unique_by_column[column]
        if unique_count > TOP_VALUE_CARDINALITY_LIMIT:
            continue

        counts = data[column].value_counts(dropna=False).head(top_n)
        values = ", ".join(f"{format_top_value(value)}: {count}" for value, count in counts.items())
        rows.append({"column": column, f"top_{top_n}_values": values})
    return pd.DataFrame(rows)


def quality_signals(data: pd.DataFrame, health: pd.DataFrame, scope_label: str) -> List[str]:
    row_count = len(data)
    lines = [f"- Duplicate rows in {scope_label}: `{int(data.duplicated().sum())}` / `{row_count}`."]

    null_heavy = health.loc[health["null_%"] >= 50, "column"].tolist()
    if null_heavy:
        lines.append(f"- Columns with >= 50% null in {scope_label}: {format_column_list(null_heavy)}.")

    near_constant = health.loc[health["unique"] <= 1, "column"].tolist()
    if near_constant:
        lines.append(f"- Near-constant columns in {scope_label}: {format_column_list(near_constant)}.")

    if row_count:
        high_cardinality = health.loc[
            health["unique"] / row_count >= HIGH_CARDINALITY_RATIO, "column"
        ].tolist()
        if high_cardinality:
            lines.append(f"- High-cardinality / ID-like columns: {format_column_list(high_cardinality)}.")

    negative_numeric = []
    numeric = data.select_dtypes(include=["number"])
    for column in numeric.columns:
        series = numeric[column].dropna()
        if not series.empty and series.min() < 0:
            negative_numeric.append(column)
    if negative_numeric:
        lines.append(f"- Numeric columns containing negative values: {format_column_list(negative_numeric)}.")

    return lines


def format_column_list(columns: List[str]) -> str:
    return ", ".join(f"`{column}`" for column in columns)


def markdown_table(df: pd.DataFrame, *, floatfmt: Optional[str] = None) -> str:
    if df.empty:
        return "_No columns matched._"
    kwargs = {"index": False}
    if floatfmt is not None:
        kwargs["floatfmt"] = floatfmt
    return df.to_markdown(**kwargs)


def build_report(
    parquet_path: Path,
    row_limit: Optional[int],
    preview_rows: int,
    time_bucket: str,
) -> str:
    parquet_file = pq.ParquetFile(parquet_path)
    metadata = parquet_file.metadata
    data = load_data(parquet_file, row_limit)
    health = column_health_table(data)
    scope_label = "full data" if row_limit is None or len(data) == metadata.num_rows else "limited data"
    section_scope = "full-data" if scope_label == "full data" else "limited-data"

    summary = pd.DataFrame(
        [
            {"metric": "file", "value": str(parquet_path.resolve())},
            {"metric": "rows", "value": metadata.num_rows},
            {"metric": "columns", "value": metadata.num_columns},
            {"metric": "row_groups", "value": metadata.num_row_groups},
            {"metric": "file_size_mb", "value": f"{parquet_path.stat().st_size / (1024 * 1024):.2f}"},
            {"metric": "rows_loaded", "value": len(data)},
        ]
    )

    sections = [
        f"# Data Overview: {parquet_path.name}",
        "## Dataset Summary",
        markdown_table(summary),
        "## Schema",
        markdown_table(parquet_schema_table(parquet_file)),
        f"## Column Health ({section_scope})",
        markdown_table(health, floatfmt=".4f"),
        f"## Numeric Statistics ({section_scope})",
        markdown_table(numeric_statistics_table(data), floatfmt=".4f"),
        f"## Datetime Coverage ({section_scope})",
        markdown_table(datetime_coverage_table(data)),
        f"## Datetime Distribution by {time_bucket.title()} ({section_scope})",
        markdown_table(datetime_distribution_table(data, bucket=time_bucket), floatfmt=".4f"),
        f"## Top Values ({section_scope}, top 5)",
        markdown_table(top_values_table(data, health, top_n=5)),
        "## Data Quality Signals",
        "\n".join(quality_signals(data, health, scope_label)),
        "## Data Preview",
        markdown_table(data.head(preview_rows)),
    ]
    return "\n\n".join(sections) + "\n"


def output_path_for(parquet_path: Path, out_dir: Path, data_root: Path) -> Path:
    try:
        relative_parent = parquet_path.resolve().parent.relative_to(data_root.resolve())
    except ValueError:
        relative_parent = Path()
    return out_dir / relative_parent / f"{parquet_path.name}.md"


def write_report(
    parquet_path: Path,
    out_dir: Path,
    data_root: Path,
    row_limit: Optional[int],
    preview_rows: int,
    time_bucket: str,
) -> Path:
    report = build_report(
        parquet_path,
        row_limit=row_limit,
        preview_rows=preview_rows,
        time_bucket=time_bucket,
    )
    out_path = output_path_for(parquet_path, out_dir, data_root)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render markdown overview reports for parquet datasets."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Parquet files or directories to scan. Defaults to experiments/data/parquets.",
    )
    parser.add_argument(
        "--data-root",
        type=Path,
        default=DEFAULT_DATA_ROOT,
        help="Root used to preserve dataset subfolders in the output path.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=DEFAULT_OUT_DIR,
        help="Directory where markdown reports are written.",
    )
    parser.add_argument(
        "--sample-rows",
        type=int,
        default=None,
        help="Limit rows loaded for faster checks. Omit this option to scan the full parquet file.",
    )
    parser.add_argument(
        "--time-bucket",
        choices=TIME_BUCKETS,
        default="day",
        help="Bucket size for timestamp distribution.",
    )
    parser.add_argument(
        "--preview-rows",
        type=int,
        default=DEFAULT_PREVIEW_ROWS,
        help="Number of rows to include in the preview section.",
    )
    args = parser.parse_args()

    paths = args.paths or [args.data_root]
    parquet_files = discover_parquet_files(paths)
    if not parquet_files:
        raise SystemExit("No parquet files found.")

    for parquet_path in parquet_files:
        out_path = write_report(
            parquet_path=parquet_path,
            out_dir=args.out_dir,
            data_root=args.data_root,
            row_limit=args.sample_rows,
            preview_rows=args.preview_rows,
            time_bucket=args.time_bucket,
        )
        print(f"[OK] {parquet_path} -> {out_path}")


if __name__ == "__main__":
    main()
