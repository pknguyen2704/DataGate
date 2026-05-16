import argparse
from pathlib import Path
from time import perf_counter

import pandas as pd


JOB_NAME = "write_bronze_table_parquet"

DROPOFF_COL = "tpep_dropoff_datetime"

# Keep only the target date_hour range after date_hour is calculated.
START_TIMESTAMP = "2025-01-01 00:00:00"
END_TIMESTAMP = "2025-01-31 23:00:00"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Read raw parquet, add date_hour and processing_date_hour, then write bronze parquet"
    )

    parser.add_argument("--input_parquet_path", required=True)
    parser.add_argument("--output_dir", default=None)
    parser.add_argument("--output_file_name", default=None)

    return parser.parse_args()


def resolve_output_path(
    input_path: str,
    output_dir: str | None,
    output_file_name: str | None,
) -> Path:
    input_path = Path(input_path)

    if not input_path.exists():
        raise FileNotFoundError(f"Input parquet file does not exist: {input_path}")

    output_dir = Path(output_dir) if output_dir else input_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    output_name = output_file_name or f"bronze_{input_path.name}"

    if not output_name.endswith(".parquet"):
        output_name += ".parquet"

    return output_dir / output_name


def add_date_hour(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate date_hour using the same rule as the old job:

    - Convert tpep_dropoff_datetime to datetime.
    - If minute >= 45, add 1 hour.
    - Floor the adjusted timestamp to hour.

    Examples:
    - 2025-01-01 10:44:59 -> 2025-01-01 10:00:00
    - 2025-01-01 10:45:00 -> 2025-01-01 11:00:00
    - 2025-01-31 23:45:00 -> 2025-02-01 00:00:00
    """
    df = df.copy()

    df[DROPOFF_COL] = pd.to_datetime(df[DROPOFF_COL], errors="coerce")

    add_hour = (df[DROPOFF_COL].dt.minute >= 45).astype(int)
    adjusted_time = df[DROPOFF_COL] + pd.to_timedelta(add_hour, unit="h")

    df["date_hour"] = adjusted_time.dt.floor("h")

    return df


def filter_date_hour(df: pd.DataFrame) -> pd.DataFrame:
    start_ts = pd.Timestamp(START_TIMESTAMP)
    end_ts = pd.Timestamp(END_TIMESTAMP)

    filtered_df = df[
        (df["date_hour"] >= start_ts)
        & (df["date_hour"] <= end_ts)
    ].copy()

    return filtered_df


def add_processing_date_hour(df: pd.DataFrame) -> pd.DataFrame:
    """
    Assign the processing batch from date_hour.

    Rule:
    - date_hour before 12:00  -> processing_date_hour = same day 12:00
    - date_hour from 12:00+   -> processing_date_hour = next day 00:00
    """
    df = df.copy()

    date_day = df["date_hour"].dt.floor("D")
    is_before_12h = df["date_hour"].dt.hour < 12

    df["processing_date_hour"] = date_day + pd.Timedelta(days=1)
    df.loc[is_before_12h, "processing_date_hour"] = date_day + pd.Timedelta(hours=12)

    return df


def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Normalize column names to match the lakehouse table schema.
    df.columns = [str(col).strip().lower() for col in df.columns]

    if DROPOFF_COL not in df.columns:
        raise ValueError(f"Missing required column: {DROPOFF_COL}")

    row_count_before = len(df)

    df = add_date_hour(df)

    invalid_date_hour_count = int(df["date_hour"].isna().sum())
    if invalid_date_hour_count > 0:
        print(
            f"[Warning] Rows with invalid {DROPOFF_COL} / date_hour: "
            f"{invalid_date_hour_count:,}"
        )

    df = filter_date_hour(df)
    df = add_processing_date_hour(df)

    row_count_after = len(df)
    removed_count = row_count_before - row_count_after
    removed_rate = removed_count / row_count_before * 100 if row_count_before > 0 else 0.0

    print("\n========== Bronze Transform Summary ==========")
    print(f"Rows before transform/filter : {row_count_before:,}")
    print(f"Rows after date_hour filter  : {row_count_after:,}")
    print(f"Rows removed by filter       : {removed_count:,}")
    print(f"Removed rate                 : {removed_rate:.2f}%")
    print("==============================================\n")

    return df


def write_to_parquet(df: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False, engine="pyarrow")


def print_overview(df: pd.DataFrame, output_path: Path) -> None:
    file_size_mb = output_path.stat().st_size / (1024 * 1024)

    print("\n========== Bronze Parquet Overview ==========")
    print(f"Output path              : {output_path}")
    print(f"File size                : {file_size_mb:.2f} MB")
    print(f"Rows                     : {len(df):,}")
    print(f"Columns                  : {len(df.columns):,}")
    print(f"Min date_hour            : {df['date_hour'].min()}")
    print(f"Max date_hour            : {df['date_hour'].max()}")
    print(f"Min processing_date_hour : {df['processing_date_hour'].min()}")
    print(f"Max processing_date_hour : {df['processing_date_hour'].max()}")

    mapping_df = (
        df[["date_hour", "processing_date_hour"]]
        .drop_duplicates()
        .sort_values(["date_hour"])
    )

    print("\nSample date_hour / processing_date_hour - HEAD:")
    print(mapping_df.head(20).to_string(index=False))

    print("\nSample date_hour / processing_date_hour - TAIL:")
    print(mapping_df.tail(20).to_string(index=False))

    print("\nSample rows - HEAD:")
    print(df.head(5).to_string(index=False))

    print("\nSample rows - TAIL:")
    print(df.tail(5).to_string(index=False))

    print("=============================================\n")


def main() -> None:
    start_time = perf_counter()
    args = parse_args()

    print(f"[{JOB_NAME}] Input parquet: {args.input_parquet_path}")

    output_path = resolve_output_path(
        input_path=args.input_parquet_path,
        output_dir=args.output_dir,
        output_file_name=args.output_file_name,
    )

    raw_df = pd.read_parquet(args.input_parquet_path)
    bronze_df = transform_data(raw_df)

    write_to_parquet(bronze_df, output_path)
    print_overview(bronze_df, output_path)

    total_seconds = perf_counter() - start_time
    print(f"[Job Completed] {JOB_NAME} finished in {total_seconds:.3f} seconds")


if __name__ == "__main__":
    main()
