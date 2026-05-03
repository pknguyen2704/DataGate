import argparse
from pathlib import Path
from time import perf_counter

import pandas as pd


JOB_NAME = "write_silver_table_parquet"

REQUIRED_COLUMNS = [
    "vendorid",
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime",
    "date_hour",
    "processing_date_hour",
]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Read bronze parquet, clean data, then write silver parquet"
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

    if output_file_name:
        output_name = output_file_name
    else:
        if input_path.name.startswith("bronze_"):
            output_name = input_path.name.replace("bronze_", "silver_", 1)
        else:
            output_name = f"silver_{input_path.name}"

    if not output_name.endswith(".parquet"):
        output_name += ".parquet"

    return output_dir / output_name


def validate_columns(df: pd.DataFrame) -> None:
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]

    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")


def convert_datetime_columns(df: pd.DataFrame) -> pd.DataFrame:
    datetime_columns = [
        "tpep_pickup_datetime",
        "tpep_dropoff_datetime",
        "date_hour",
        "processing_date_hour",
    ]

    for col in datetime_columns:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    return df


def print_required_null_summary(df: pd.DataFrame) -> None:
    total_rows = len(df)

    null_summary = (
        df[REQUIRED_COLUMNS]
        .isna()
        .sum()
        .sort_values(ascending=False)
    )

    null_summary = null_summary[null_summary > 0]

    print("\n========== Required Column Null Summary ==========")

    if null_summary.empty:
        print("No null values found in required columns.")
    else:
        for col, null_count in null_summary.items():
            null_rate = null_count / total_rows * 100 if total_rows > 0 else 0
            print(f"{col:<30} {null_count:>12,} rows ({null_rate:>6.2f}%)")

    print("==================================================\n")


def print_issue_summary(df: pd.DataFrame, issue_masks: dict) -> None:
    total_rows = len(df)

    print("\n========== Data Quality Issue Summary ==========")

    for issue_name, mask in issue_masks.items():
        issue_count = int(mask.sum())
        issue_rate = issue_count / total_rows * 100 if total_rows > 0 else 0

        print(
            f"{issue_name:<35} "
            f"{issue_count:>12,} rows "
            f"({issue_rate:>6.2f}%)"
        )

    any_issue_mask = pd.Series(False, index=df.index)

    for mask in issue_masks.values():
        any_issue_mask = any_issue_mask | mask

    total_issue_rows = int(any_issue_mask.sum())
    total_issue_rate = total_issue_rows / total_rows * 100 if total_rows > 0 else 0

    print("-----------------------------------------------")
    print(
        f"{'Total rows with any issue':<35} "
        f"{total_issue_rows:>12,} rows "
        f"({total_issue_rate:>6.2f}%)"
    )
    print("================================================\n")


def print_sequential_cleaning_summary(df: pd.DataFrame, issue_masks: dict) -> None:
    current_mask = pd.Series(True, index=df.index)

    print("\n========== Sequential Cleaning Summary ==========")

    for issue_name, mask in issue_masks.items():
        removed_now = current_mask & mask
        removed_count = int(removed_now.sum())
        removed_rate = removed_count / len(df) * 100 if len(df) > 0 else 0

        print(
            f"{issue_name:<35} "
            f"removed now: {removed_count:>12,} rows "
            f"({removed_rate:>6.2f}%)"
        )

        current_mask = current_mask & ~mask

    print("-----------------------------------------------")
    print(f"Rows remaining after all steps: {int(current_mask.sum()):,}")
    print("================================================\n")


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [col.lower() for col in df.columns]

    validate_columns(df)

    row_count_before = len(df)

    df = convert_datetime_columns(df)

    df["trip_duration_min"] = (
        df["tpep_dropoff_datetime"] - df["tpep_pickup_datetime"]
    ).dt.total_seconds() / 60

    null_required_mask = df[REQUIRED_COLUMNS].isna().any(axis=1)

    invalid_duration_mask = (
        (df["trip_duration_min"] < 0)
    )

    invalid_trip_distance_mask = (
        (df["trip_distance"] < 0)
    )

    invalid_passenger_count_mask = (
        (df["passenger_count"] < 0)
    )

    invalid_fare_amount_mask = (
        (df["fare_amount"] < 0)
    )

    invalid_total_amount_mask = (
        (df["total_amount"] < 0)
    )

    duplicate_mask = df.duplicated()

    issue_masks = {
        "Null in required columns": null_required_mask,
        "Invalid trip duration < 0": invalid_duration_mask,
        "Invalid trip_distance < 0": invalid_trip_distance_mask,
        "Invalid passenger_count < 0": invalid_passenger_count_mask,
        "Invalid fare_amount < 0": invalid_fare_amount_mask,
        "Invalid total_amount < 0": invalid_total_amount_mask,
        "Duplicate rows": duplicate_mask,
    }

    print_required_null_summary(df)
    print_issue_summary(df, issue_masks)
    print_sequential_cleaning_summary(df, issue_masks)

    valid_mask = (
        ~null_required_mask
        & ~invalid_duration_mask
        & ~invalid_trip_distance_mask
        & ~invalid_passenger_count_mask
        & ~invalid_fare_amount_mask
        & ~invalid_total_amount_mask
        & ~duplicate_mask
    )

    cleaned_df = df[valid_mask].copy()

    row_count_after = len(cleaned_df)
    removed_count = row_count_before - row_count_after
    removed_rate = removed_count / row_count_before * 100 if row_count_before > 0 else 0

    print("\n========== Silver Cleaning Summary ==========")
    print(f"Rows before clean : {row_count_before:,}")
    print(f"Rows after clean  : {row_count_after:,}")
    print(f"Rows removed      : {removed_count:,}")
    print(f"Removed rate      : {removed_rate:.2f}%")
    print("=============================================\n")

    return cleaned_df


def write_to_parquet(df: pd.DataFrame, output_path: Path) -> None:
    df.to_parquet(output_path, index=False, engine="pyarrow")


def print_overview(df: pd.DataFrame, output_path: Path) -> None:
    file_size_mb = output_path.stat().st_size / (1024 * 1024)

    print("\n========== Silver Parquet Overview ==========")
    print(f"Output path              : {output_path}")
    print(f"File size                : {file_size_mb:.2f} MB")
    print(f"Rows                     : {len(df):,}")
    print(f"Columns                  : {len(df.columns):,}")
    print(f"Min date_hour            : {df['date_hour'].min()}")
    print(f"Max date_hour            : {df['date_hour'].max()}")
    print(f"Min processing_date_hour : {df['processing_date_hour'].min()}")
    print(f"Max processing_date_hour : {df['processing_date_hour'].max()}")

    null_count = df.isna().sum()
    null_count = null_count[null_count > 0]

    print("\nNull values after clean:")
    if null_count.empty:
        print("No null values found.")
    else:
        print(null_count.sort_values(ascending=False).to_string())

    print("\nSample rows - HEAD:")
    print(df.head(5).to_string(index=False))

    print("\nSample rows - TAIL:")
    print(df.tail(5).to_string(index=False))

    print("=============================================\n")


def main() -> None:
    start_time = perf_counter()
    args = parse_args()

    print(f"[{JOB_NAME}] Input bronze parquet: {args.input_parquet_path}")

    output_path = resolve_output_path(
        input_path=args.input_parquet_path,
        output_dir=args.output_dir,
        output_file_name=args.output_file_name,
    )

    bronze_df = pd.read_parquet(args.input_parquet_path)

    silver_df = clean_data(bronze_df)

    write_to_parquet(silver_df, output_path)

    print_overview(silver_df, output_path)

    total_seconds = perf_counter() - start_time

    print(f"[Job Completed] {JOB_NAME} finished in {total_seconds:.3f} seconds")


if __name__ == "__main__":
    main()