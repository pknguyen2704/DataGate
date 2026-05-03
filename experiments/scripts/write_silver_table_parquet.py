import argparse
from pathlib import Path
from time import perf_counter

import pandas as pd


JOB_NAME = "write_silver_table_parquet"

# -----------------------------------------------------------------------------
# Expected columns
# -----------------------------------------------------------------------------

# Columns from TLC Yellow Taxi data dictionary.
# This job normalizes all input column names to lowercase.
TLC_COLUMNS = [
    "vendorid",
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime",
    "passenger_count",
    "trip_distance",
    "ratecodeid",
    "store_and_fwd_flag",
    "pulocationid",
    "dolocationid",
    "payment_type",
    "fare_amount",
    "extra",
    "mta_tax",
    "tip_amount",
    "tolls_amount",
    "improvement_surcharge",
    "total_amount",
    "congestion_surcharge",
    "airport_fee",
    "cbd_congestion_fee",
]

# These two columns are created in Bronze.
# Important: Silver DOES NOT recompute these columns.
BRONZE_BATCH_COLUMNS = [
    "date_hour",
    "processing_date_hour",
]

EXPECTED_COLUMNS = TLC_COLUMNS + BRONZE_BATCH_COLUMNS

# Rows missing these columns are not reliable enough for Silver.
# Optional fields can still be null and are only reported.
CRITICAL_NOT_NULL_COLUMNS = [
    "vendorid",
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime",
    "trip_distance",
    "pulocationid",
    "dolocationid",
    "fare_amount",
    "total_amount",
    "date_hour",
    "processing_date_hour",
]

DATETIME_COLUMNS = [
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime",
    "date_hour",
    "processing_date_hour",
]

NUMERIC_COLUMNS = [
    "vendorid",
    "passenger_count",
    "trip_distance",
    "ratecodeid",
    "pulocationid",
    "dolocationid",
    "payment_type",
    "fare_amount",
    "extra",
    "mta_tax",
    "tip_amount",
    "tolls_amount",
    "improvement_surcharge",
    "total_amount",
    "congestion_surcharge",
    "airport_fee",
    "cbd_congestion_fee",
]

# Valid domain values from TLC Yellow Taxi data dictionary.
VALID_VENDOR_IDS = {1, 2, 6, 7}
VALID_RATECODE_IDS = {1, 2, 3, 4, 5, 6, 99}
VALID_PAYMENT_TYPES = {0, 1, 2, 3, 4, 5, 6}
VALID_STORE_AND_FWD_FLAGS = {"Y", "N"}


# -----------------------------------------------------------------------------
# CLI / path helpers
# -----------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="Read bronze parquet, clean valid rows, then write silver parquet"
    )

    # Keep the same input parameters as the original version.
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


# -----------------------------------------------------------------------------
# Basic helpers
# -----------------------------------------------------------------------------

def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(col).strip().lower() for col in df.columns]
    return df


def validate_expected_columns(df: pd.DataFrame) -> None:
    missing_columns = [col for col in EXPECTED_COLUMNS if col not in df.columns]

    if missing_columns:
        raise ValueError(
            "Missing expected columns for Yellow Taxi Bronze -> Silver cleaning: "
            f"{missing_columns}"
        )


def convert_column_types(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    for col in DATETIME_COLUMNS:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    for col in NUMERIC_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Normalize store_and_fwd_flag, but do not fill null because the dictionary
    # only defines Y/N and does not define an unknown code for this column.
    df["store_and_fwd_flag"] = (
        df["store_and_fwd_flag"]
        .astype("string")
        .str.strip()
        .str.upper()
    )
    df.loc[
        df["store_and_fwd_flag"].isin(["", "<NA>", "NAN", "NONE", "NULL"]),
        "store_and_fwd_flag",
    ] = pd.NA

    # Dictionary-based normalization:
    # - RatecodeID 99 means Null/unknown.
    # - payment_type 5 means Unknown.
    df.loc[df["ratecodeid"].isna(), "ratecodeid"] = 99
    df.loc[df["payment_type"].isna(), "payment_type"] = 5

    return df


def build_null_summary(df: pd.DataFrame) -> pd.DataFrame:
    total_rows = len(df)
    rows = []

    for col in df.columns:
        null_count = int(df[col].isna().sum())
        null_rate = null_count / total_rows * 100 if total_rows > 0 else 0.0
        rows.append(
            {
                "column_name": col,
                "null_count": null_count,
                "null_rate_pct": null_rate,
            }
        )

    return pd.DataFrame(rows).sort_values(
        ["null_count", "column_name"], ascending=[False, True]
    )


def build_issue_summary(df: pd.DataFrame, issue_masks: dict[str, pd.Series]) -> pd.DataFrame:
    total_rows = len(df)
    rows = []

    for issue_name, mask in issue_masks.items():
        mask = mask.fillna(False)
        issue_count = int(mask.sum())
        issue_rate = issue_count / total_rows * 100 if total_rows > 0 else 0.0
        rows.append(
            {
                "issue_name": issue_name,
                "issue_count": issue_count,
                "issue_rate_pct": issue_rate,
            }
        )

    any_issue_mask = pd.Series(False, index=df.index)
    for mask in issue_masks.values():
        any_issue_mask = any_issue_mask | mask.fillna(False)

    rows.append(
        {
            "issue_name": "Total rows removed from Silver",
            "issue_count": int(any_issue_mask.sum()),
            "issue_rate_pct": int(any_issue_mask.sum()) / total_rows * 100 if total_rows > 0 else 0.0,
        }
    )

    return pd.DataFrame(rows)


def build_sequential_cleaning_summary(
    df: pd.DataFrame,
    issue_masks: dict[str, pd.Series],
) -> pd.DataFrame:
    current_valid_mask = pd.Series(True, index=df.index)
    rows = []

    for issue_name, mask in issue_masks.items():
        mask = mask.fillna(False)
        removed_now = current_valid_mask & mask
        current_valid_mask = current_valid_mask & ~mask

        rows.append(
            {
                "cleaning_step": issue_name,
                "removed_now": int(removed_now.sum()),
                "removed_rate_pct_of_original": int(removed_now.sum()) / len(df) * 100 if len(df) > 0 else 0.0,
                "remaining_after_step": int(current_valid_mask.sum()),
            }
        )

    return pd.DataFrame(rows)


def print_dataframe(title: str, df: pd.DataFrame) -> None:
    print(f"\n========== {title} ==========")
    if df.empty:
        print("No records.")
    else:
        print(df.to_string(index=False))
    print("=" * (len(title) + 22))


def print_domain_summary(df: pd.DataFrame) -> None:
    print("\n========== Domain Value Summary ==========")

    for col in ["vendorid", "ratecodeid", "payment_type", "store_and_fwd_flag"]:
        print(f"\n{col} value counts:")
        print(df[col].value_counts(dropna=False).sort_index().to_string())

    print("==========================================\n")


# -----------------------------------------------------------------------------
# Cleaning logic
# -----------------------------------------------------------------------------

def build_blocking_issue_masks(df: pd.DataFrame) -> dict[str, pd.Series]:
    trip_duration_min = (
        df["tpep_dropoff_datetime"] - df["tpep_pickup_datetime"]
    ).dt.total_seconds() / 60

    null_critical_mask = df[CRITICAL_NOT_NULL_COLUMNS].isna().any(axis=1)

    invalid_duration_mask = trip_duration_min.notna() & (trip_duration_min < 0)

    invalid_vendorid_mask = df["vendorid"].notna() & ~df["vendorid"].isin(VALID_VENDOR_IDS)
    invalid_ratecodeid_mask = df["ratecodeid"].notna() & ~df["ratecodeid"].isin(VALID_RATECODE_IDS)
    invalid_payment_type_mask = df["payment_type"].notna() & ~df["payment_type"].isin(VALID_PAYMENT_TYPES)
    invalid_store_and_fwd_flag_mask = (
        df["store_and_fwd_flag"].notna()
        & ~df["store_and_fwd_flag"].isin(VALID_STORE_AND_FWD_FLAGS)
    )

    invalid_trip_distance_mask = df["trip_distance"].notna() & (df["trip_distance"] < 0)
    invalid_passenger_count_mask = df["passenger_count"].notna() & (df["passenger_count"] < 0)

    invalid_location_mask = (
        df["pulocationid"].notna()
        & df["dolocationid"].notna()
        & ((df["pulocationid"] <= 0) | (df["dolocationid"] <= 0))
    )

    invalid_fare_amount_mask = df["fare_amount"].notna() & (df["fare_amount"] < 0)
    invalid_total_amount_mask = df["total_amount"].notna() & (df["total_amount"] < 0)

    duplicate_mask = df.duplicated(subset=EXPECTED_COLUMNS, keep="first")

    return {
        "Null in critical columns": null_critical_mask,
        "Invalid trip duration < 0": invalid_duration_mask,
        "Invalid VendorID domain": invalid_vendorid_mask,
        "Invalid RatecodeID domain": invalid_ratecodeid_mask,
        "Invalid payment_type domain": invalid_payment_type_mask,
        "Invalid store_and_fwd_flag domain": invalid_store_and_fwd_flag_mask,
        "Invalid trip_distance < 0": invalid_trip_distance_mask,
        "Invalid passenger_count < 0": invalid_passenger_count_mask,
        "Invalid PULocationID/DOLocationID <= 0": invalid_location_mask,
        "Invalid fare_amount < 0": invalid_fare_amount_mask,
        "Invalid total_amount < 0": invalid_total_amount_mask,
        "Duplicate rows": duplicate_mask,
    }


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_column_names(df)
    validate_expected_columns(df)

    row_count_before = len(df)

    df = convert_column_types(df)

    # Important: date_hour and processing_date_hour are only converted to datetime.
    # They are NOT recomputed in Silver.
    issue_masks = build_blocking_issue_masks(df)

    null_summary = build_null_summary(df)
    issue_summary = build_issue_summary(df, issue_masks)
    sequential_summary = build_sequential_cleaning_summary(df, issue_masks)

    print_dataframe("Null Summary - All Columns", null_summary)
    print_dataframe("Blocking Data Quality Issue Summary", issue_summary)
    print_dataframe("Sequential Cleaning Summary", sequential_summary)
    print_domain_summary(df)

    invalid_mask = pd.Series(False, index=df.index)
    for mask in issue_masks.values():
        invalid_mask = invalid_mask | mask.fillna(False)

    silver_df = df[~invalid_mask].copy()

    row_count_after = len(silver_df)
    removed_count = row_count_before - row_count_after
    removed_rate = removed_count / row_count_before * 100 if row_count_before > 0 else 0.0

    print("\n========== Silver Cleaning Summary ==========")
    print(f"Rows before clean : {row_count_before:,}")
    print(f"Rows after clean  : {row_count_after:,}")
    print(f"Rows removed      : {removed_count:,}")
    print(f"Removed rate      : {removed_rate:.2f}%")
    print("=============================================\n")

    # Keep stable column order. Keep any extra input columns after expected columns.
    extra_columns = [col for col in silver_df.columns if col not in EXPECTED_COLUMNS]
    silver_df = silver_df[EXPECTED_COLUMNS + extra_columns]

    return silver_df


# -----------------------------------------------------------------------------
# IO / overview
# -----------------------------------------------------------------------------

def write_to_parquet(df: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
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
