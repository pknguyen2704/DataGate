import argparse
from pathlib import Path

import numpy as np
import pandas as pd


PROFILE_COLS = [
    "trip_distance",
    "fare_amount",
    "total_amount",
    "PULocationID",
    "DOLocationID",
    "store_and_fwd_flag",
]


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--file", required=True)
    parser.add_argument("--output-file", required=True)
    parser.add_argument("--event-col", default="tpep_dropoff_datetime")
    parser.add_argument("--dirty-date-hours", required=True)
    parser.add_argument("--dirty-ratio", type=float, required=True)
    parser.add_argument("--dirty-seed", type=int, default=2025)
    parser.add_argument("--overwrite", action="store_true")

    args = parser.parse_args()

    args.file = Path(args.file)
    args.output_file = Path(args.output_file)

    # Allow both 0.3 and 30 for 30%
    if args.dirty_ratio > 1:
        args.dirty_ratio = args.dirty_ratio / 100

    if args.dirty_ratio < 0 or args.dirty_ratio > 1:
        raise ValueError("--dirty-ratio must be between 0 and 1, or 0 and 100.")

    args.dirty_date_hours = [
        pd.to_datetime(x.strip())
        for x in args.dirty_date_hours.split(",")
        if x.strip()
    ]

    return args


def get_date_hour(df, event_col):
    """
    Create date_hour from event time.
    If minute >= 45, move to next hour.
    """
    event_time = pd.to_datetime(df[event_col])

    add_hour = (event_time.dt.minute >= 45).astype(int)
    date_hour = event_time + pd.to_timedelta(add_hour, unit="h")

    return date_hour.dt.floor("h")


def get_window(batch_time):
    """
    Convert processing batch time to real data window.

    2025-01-27 12:00:00 -> [2025-01-27 00:00:00, 2025-01-27 12:00:00)
    2025-01-28 00:00:00 -> [2025-01-27 12:00:00, 2025-01-28 00:00:00)
    """
    if batch_time.hour == 12:
        start_time = batch_time.normalize()
        end_time = batch_time

    elif batch_time.hour == 0:
        start_time = batch_time - pd.Timedelta(hours=12)
        end_time = batch_time

    else:
        raise ValueError(f"Only support 00:00 and 12:00 batch: {batch_time}")

    return start_time, end_time


def build_dirty_mask(date_hour, dirty_date_hours):
    """
    Select rows belonging to all dirty batch windows.
    """
    mask = pd.Series(False, index=date_hour.index)

    print("\n[DIRTY WINDOWS]")

    for batch_time in dirty_date_hours:
        start_time, end_time = get_window(batch_time)

        one_window_mask = (date_hour >= start_time) & (date_hour < end_time)
        mask = mask | one_window_mask

        print(
            f"- {batch_time} covers [{start_time}, {end_time}) "
            f"| rows={one_window_mask.sum()}"
        )

    return mask


def profile(df, title):
    """
    Print simple profile for selected columns.
    """
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)

    rows = []

    for col in PROFILE_COLS:
        if col not in df.columns:
            continue

        s = df[col]
        num = pd.to_numeric(s, errors="coerce")
        text_len = s.dropna().astype(str).str.len()

        rows.append({
            "column": col,
            "rows": len(s),
            "nulls": s.isna().sum(),
            "unique": s.nunique(dropna=True),
            "min": num.min() if num.notna().any() else None,
            "max": num.max() if num.notna().any() else None,
            "mean": num.mean() if num.notna().any() else None,
            "std": num.std() if num.notna().any() else None,
            "min_length": text_len.min() if len(text_len) > 0 else None,
            "max_length": text_len.max() if len(text_len) > 0 else None,
        })

    print(pd.DataFrame(rows).to_string(index=False))


def dirty_numeric_col(df, dirty_rows, selected_before, col, factor=10):
    """
    Make numeric values abnormally large based on real max value.
    """
    if col not in df.columns:
        return

    real_max = pd.to_numeric(selected_before[col], errors="coerce").abs().max()

    if pd.isna(real_max) or real_max == 0:
        real_max = 1

    current = pd.to_numeric(df.loc[dirty_rows, col], errors="coerce")
    current = current.abs().fillna(0)

    df.loc[dirty_rows, col] = current + real_max * factor

    print(f"[DIRTY] {col}: current + {real_max} * {factor}")


def dirty_fixed_value(df, dirty_rows, col, value):
    """
    Set selected rows to one abnormal fixed value.
    """
    if col not in df.columns:
        return

    df.loc[dirty_rows, col] = value

    print(f"[DIRTY] {col}: set to {value}")


def main():
    args = parse_args()

    if args.output_file.exists() and not args.overwrite:
        raise FileExistsError(f"Output file exists: {args.output_file}")

    print(f"[READ] {args.file}")
    df = pd.read_parquet(args.file)

    date_hour = get_date_hour(df, args.event_col)

    dirty_mask = build_dirty_mask(
        date_hour=date_hour,
        dirty_date_hours=args.dirty_date_hours,
    )

    selected_rows = df.index[dirty_mask]

    if len(selected_rows) == 0:
        raise ValueError("No rows found in selected dirty windows.")

    dirty_count = round(len(selected_rows) * args.dirty_ratio)

    if dirty_count == 0 and args.dirty_ratio > 0:
        dirty_count = 1

    rng = np.random.default_rng(args.dirty_seed)

    dirty_rows = rng.choice(
        selected_rows.to_numpy(),
        size=dirty_count,
        replace=False,
    )

    print("\n[INFO]")
    print(f"Total rows: {len(df)}")
    print(f"Rows in dirty windows: {len(selected_rows)}")
    print(f"Rows to dirty: {dirty_count}")
    print(f"Dirty ratio: {args.dirty_ratio}")

    selected_before = df.loc[selected_rows].copy()

    profile(selected_before, "PROFILE BEFORE DIRTY DATA")

    df_dirty = df.copy()

    # Make important numeric columns abnormal
    dirty_numeric_col(df_dirty, dirty_rows, selected_before, "trip_distance", factor=10)
    dirty_numeric_col(df_dirty, dirty_rows, selected_before, "fare_amount", factor=10)
    dirty_numeric_col(df_dirty, dirty_rows, selected_before, "total_amount", factor=10)

    # Make location ids abnormal
    dirty_fixed_value(df_dirty, dirty_rows, "PULocationID", 999)
    dirty_fixed_value(df_dirty, dirty_rows, "DOLocationID", 999)

    # Change categorical distribution
    dirty_fixed_value(df_dirty, dirty_rows, "store_and_fwd_flag", "Y")

    selected_after = df_dirty.loc[selected_rows].copy()

    profile(selected_after, "PROFILE AFTER DIRTY DATA")

    print(f"\n[WRITE] {args.output_file}")
    args.output_file.parent.mkdir(parents=True, exist_ok=True)
    df_dirty.to_parquet(args.output_file, index=False)

    print("\n[DONE]")
    print(f"Saved dirty file to: {args.output_file}")


if __name__ == "__main__":
    main()