import argparse
import time
from pathlib import Path
from typing import List, Optional, Set, Tuple

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from tqdm import tqdm


DEFAULT_OUTPUT_DIR = Path("experiments/data/tlc_yellow_tripdata")


def parse_list_arg(value: Optional[str]) -> List[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_dirty_dates(value: Optional[str]) -> Set[pd.Timestamp]:
    return {pd.to_datetime(item).normalize() for item in parse_list_arg(value)}


def parse_dirty_date_hours(value: Optional[str]) -> Set[pd.Timestamp]:
    return {pd.to_datetime(item) for item in parse_list_arg(value)}


def normalize_ratio(value: float) -> float:
    ratio = float(value)
    if ratio > 1:
        ratio = ratio / 100.0
    if ratio < 0 or ratio > 1:
        raise ValueError("--dirty-ratio phải nằm trong [0, 1] hoặc [0, 100].")
    return ratio


def parse_args():
    parser = argparse.ArgumentParser(
        description="Tạo parquet dirty từ parquet gốc TLC yellow tripdata."
    )

    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--file", help="Đường dẫn parquet gốc.")
    source.add_argument("--data-dir", help="Thư mục chứa các file parquet gốc.")

    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Thư mục ghi parquet dirty khi xử lý một hoặc nhiều file.",
    )
    parser.add_argument(
        "--output-file",
        help="File parquet dirty đầu ra. Chỉ dùng khi truyền --file.",
    )
    parser.add_argument(
        "--suffix",
        default="_dirty",
        help="Hậu tố tên file output khi không truyền --output-file.",
    )
    parser.add_argument(
        "--event-col",
        default="tpep_dropoff_datetime",
        help="Cột thời gian dùng để tính date_hour.",
    )
    parser.add_argument(
        "--target-date-hour",
        help="YYYY-MM-DD HH:00:00. Nếu truyền, chỉ ghi các dòng thuộc date_hour này.",
    )
    parser.add_argument(
        "--dirty-dates",
        default="",
        help="Danh sách ngày cần làm bẩn, ví dụ '2025-01-20,2025-01-21'.",
    )
    parser.add_argument(
        "--dirty-date-hours",
        default="",
        help=(
            "Danh sách batch cần làm bẩn, ví dụ '2025-01-27 12:00:00'. "
            "Batch 12:00 làm bẩn 00:00-11:00 cùng ngày; "
            "batch 00:00 làm bẩn 12:00-23:00 ngày trước."
        ),
    )
    parser.add_argument(
        "--dirty-ratio",
        type=float,
        required=True,
        help="Tỷ lệ dòng bị làm bẩn. Ví dụ 0.3 hoặc 30 là 30 phần trăm.",
    )
    parser.add_argument("--dirty-seed", type=int, default=2025)
    parser.add_argument("--batch-size", type=int, default=100_000)
    parser.add_argument("--overwrite", action="store_true")

    args = parser.parse_args()
    args.dirty_ratio = normalize_ratio(args.dirty_ratio)
    args.dirty_dates = parse_dirty_dates(args.dirty_dates)
    args.dirty_date_hours = parse_dirty_date_hours(args.dirty_date_hours)

    if args.output_file and not args.file:
        raise ValueError("--output-file chỉ dùng được khi truyền --file.")

    if args.dirty_ratio > 0 and not args.dirty_dates and not args.dirty_date_hours:
        raise ValueError(
            "Bạn đã truyền --dirty-ratio > 0 nhưng chưa truyền "
            "--dirty-dates hoặc --dirty-date-hours."
        )

    return args


def collect_files(args) -> List[Path]:
    if args.file:
        return [Path(args.file)]

    files = sorted(Path(args.data_dir).glob("*.parquet"))
    if not files:
        raise FileNotFoundError(f"No parquet files found in {args.data_dir}")
    return files


def output_path_for(input_file: Path, args) -> Path:
    if args.output_file:
        return Path(args.output_file)

    output_dir = Path(args.output_dir)
    return output_dir / f"{input_file.stem}{args.suffix}{input_file.suffix}"


def compute_date_hour(df: pd.DataFrame, event_col: str) -> pd.Series:
    if event_col not in df.columns:
        raise ValueError(f"Không tìm thấy event column: {event_col}")

    event_time = pd.to_datetime(df[event_col])
    add_hour = (event_time.dt.minute >= 45).astype(int)
    processing_time = event_time + pd.to_timedelta(add_hour, unit="h")
    return processing_time.dt.floor("h")


def find_col_case_insensitive(df: pd.DataFrame, expected_name: str) -> Optional[str]:
    expected_lower = expected_name.lower()
    for col in df.columns:
        if col.lower() == expected_lower:
            return col
    return None


def build_dirty_batch_mask(
    date_hour: pd.Series,
    dirty_date_hours: Set[pd.Timestamp],
) -> pd.Series:
    mask = pd.Series(False, index=date_hour.index)

    for batch_time in dirty_date_hours:
        batch_time = pd.to_datetime(batch_time)

        if batch_time.minute != 0 or batch_time.second != 0:
            raise ValueError(f"--dirty-date-hours phải là đầu giờ: {batch_time}")

        if batch_time.hour == 12:
            start_time = batch_time.normalize()
            end_time = batch_time
        elif batch_time.hour == 0:
            end_time = batch_time
            start_time = batch_time - pd.Timedelta(hours=12)
        else:
            raise ValueError(
                f"--dirty-date-hours chỉ hỗ trợ batch 00:00 hoặc 12:00: {batch_time}"
            )

        mask |= (date_hour >= start_time) & (date_hour < end_time)

    return mask


def inject_dirty_data_pandas(
    df: pd.DataFrame,
    date_hour: pd.Series,
    dirty_dates: Set[pd.Timestamp],
    dirty_date_hours: Set[pd.Timestamp],
    dirty_ratio: float,
    rng: np.random.Generator,
) -> Tuple[pd.DataFrame, int]:
    if dirty_ratio <= 0:
        return df, 0

    date_hour = pd.to_datetime(date_hour)
    dirty_mask = pd.Series(False, index=df.index)

    if dirty_dates:
        dirty_mask |= date_hour.dt.normalize().isin(dirty_dates)

    if dirty_date_hours:
        dirty_mask |= build_dirty_batch_mask(date_hour, dirty_date_hours)

    eligible_idx = df.index[dirty_mask].to_numpy()
    if len(eligible_idx) == 0:
        return df, 0

    n_dirty = int(round(len(eligible_idx) * dirty_ratio))
    if n_dirty == 0:
        n_dirty = 1
    n_dirty = min(n_dirty, len(eligible_idx))

    dirty_idx = rng.choice(eligible_idx, size=n_dirty, replace=False)
    dirty_groups = rng.integers(low=0, high=5, size=n_dirty)

    df = df.copy()

    def selected(group_id: int):
        return dirty_idx[dirty_groups == group_id]

    trip_distance_col = find_col_case_insensitive(df, "trip_distance")
    if trip_distance_col is not None:
        idx = selected(0)
        if len(idx) > 0:
            df.loc[idx, trip_distance_col] = (
                pd.to_numeric(df.loc[idx, trip_distance_col], errors="coerce") * 5.0
            )

    total_amount_col = find_col_case_insensitive(df, "total_amount")
    if total_amount_col is not None:
        idx = selected(1)
        if len(idx) > 0:
            df.loc[idx, total_amount_col] = (
                pd.to_numeric(df.loc[idx, total_amount_col], errors="coerce") * 4.0
            )

    fare_amount_col = find_col_case_insensitive(df, "fare_amount")
    if fare_amount_col is not None:
        idx = selected(2)
        if len(idx) > 0:
            df.loc[idx, fare_amount_col] = (
                pd.to_numeric(df.loc[idx, fare_amount_col], errors="coerce") * 4.0
            )

    store_flag_col = find_col_case_insensitive(df, "store_and_fwd_flag")
    if store_flag_col is not None:
        idx = selected(3)
        if len(idx) > 0:
            df.loc[idx, store_flag_col] = "X"

    idx = selected(4)
    if len(idx) > 0:
        pu_location_col = find_col_case_insensitive(df, "PULocationID")
        do_location_col = find_col_case_insensitive(df, "DOLocationID")

        if pu_location_col is not None:
            df.loc[idx, pu_location_col] = 999
        if do_location_col is not None:
            df.loc[idx, do_location_col] = 999

    return df, n_dirty


def write_table(
    writer: Optional[pq.ParquetWriter],
    output_file: Path,
    df: pd.DataFrame,
    schema: pa.Schema,
):
    df = df.loc[:, schema.names]
    table = pa.Table.from_pandas(
        df,
        schema=schema,
        preserve_index=False,
        safe=False,
    )
    if writer is None:
        writer = pq.ParquetWriter(output_file, schema, compression="snappy")
    writer.write_table(table)
    return writer


def process_file(input_file: Path, output_file: Path, args) -> Tuple[int, int]:
    if output_file.exists() and not args.overwrite:
        raise FileExistsError(f"Output file exists: {output_file}. Dùng --overwrite.")

    output_file.parent.mkdir(parents=True, exist_ok=True)

    print(f"[PROCESS] {input_file}")
    print(f"[OUTPUT]  {output_file}")
    print(
        "[DIRTY]   "
        f"ratio={args.dirty_ratio:.4f} | "
        f"dirty_dates={sorted(str(x.date()) for x in args.dirty_dates)} | "
        f"dirty_date_hours={sorted(str(x) for x in args.dirty_date_hours)} | "
        f"seed={args.dirty_seed}"
    )

    parquet_file = pq.ParquetFile(input_file)
    total_rows = parquet_file.metadata.num_rows
    output_schema = parquet_file.schema_arrow
    target_dt = pd.to_datetime(args.target_date_hour) if args.target_date_hour else None
    rng = np.random.default_rng(int(args.dirty_seed))

    writer = None
    written = 0
    dirtied = 0

    try:
        with tqdm(total=total_rows) as pbar:
            for batch in parquet_file.iter_batches(batch_size=args.batch_size):
                df = batch.to_pandas()
                raw_len = len(df)
                pbar.update(raw_len)

                if df.empty:
                    continue

                date_hour = compute_date_hour(df, args.event_col)

                if target_dt is not None:
                    keep_mask = date_hour == target_dt
                    df = df[keep_mask]
                    date_hour = date_hour[keep_mask]

                if df.empty:
                    continue

                df, dirty_count = inject_dirty_data_pandas(
                    df=df,
                    date_hour=date_hour,
                    dirty_dates=args.dirty_dates,
                    dirty_date_hours=args.dirty_date_hours,
                    dirty_ratio=args.dirty_ratio,
                    rng=rng,
                )

                writer = write_table(writer, output_file, df, output_schema)
                written += len(df)
                dirtied += dirty_count
    finally:
        if writer is not None:
            writer.close()

    if written == 0:
        raise RuntimeError(f"No rows written for {input_file}")

    print(f"[DONE] written={written} | dirtied={dirtied}")
    return written, dirtied


def main():
    args = parse_args()
    files = collect_files(args)

    total_written = 0
    total_dirtied = 0
    start = time.time()

    for input_file in files:
        written, dirtied = process_file(
            input_file=input_file,
            output_file=output_path_for(input_file, args),
            args=args,
        )
        total_written += written
        total_dirtied += dirtied

    print("\n=======================")
    print(f"Total written: {total_written}")
    print(f"Total dirtied: {total_dirtied}")
    print(f"Time: {time.time() - start:.2f}s")
    print("=======================")


if __name__ == "__main__":
    main()
