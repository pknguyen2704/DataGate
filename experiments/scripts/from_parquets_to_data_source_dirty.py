


import pandas as pd
import numpy as np
import argparse
import time
from pathlib import Path
from typing import List, Optional, Set, Tuple
from tqdm import tqdm
import pyarrow.parquet as pq
import psycopg2
import io
from urllib.parse import urlparse
import os
from dotenv import load_dotenv


# ============================================================
# Database
# ============================================================

def parse_db_url(db_url):
    url = urlparse(db_url)
    return {
        "dbname": url.path[1:],
        "user": url.username,
        "password": url.password,
        "host": url.hostname,
        "port": url.port,
    }


def get_db_url():
    load_dotenv()
    return (
        f"postgresql://{os.getenv('POSTGRES_USER', 'admin')}:"
        f"{os.getenv('POSTGRES_PASSWORD', 'postgrespassword')}@"
        f"{os.getenv('POSTGRES_HOST', 'localhost')}:"
        f"{os.getenv('POSTGRES_PORT', '5433')}/"
        f"{os.getenv('POSTGRES_DB', 'postgres')}"
    )


def copy_to_postgres(df, db_url, table_name):
    conn = psycopg2.connect(**parse_db_url(db_url))
    cursor = conn.cursor()

    buffer = io.StringIO()
    df.to_csv(buffer, index=False, header=False)
    buffer.seek(0)

    cursor.copy_expert(
        f"COPY {table_name} FROM STDIN WITH CSV",
        buffer
    )

    conn.commit()
    cursor.close()
    conn.close()


# ============================================================
# Argument parsing
# ============================================================

def parse_list_arg(value: Optional[str]) -> List[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_dirty_dates(value: Optional[str]) -> Set[pd.Timestamp]:
    """
    Ví dụ:
    --dirty-dates "2025-01-20,2025-01-21"

    Ý nghĩa:
    Làm bẩn toàn bộ dòng có date_hour thuộc các ngày đó.
    """
    dates = set()

    for item in parse_list_arg(value):
        dates.add(pd.to_datetime(item).normalize())

    return dates


def parse_dirty_date_hours(value: Optional[str]) -> Set[pd.Timestamp]:
    """
    Ví dụ:
    --dirty-date-hours "2025-01-20 12:00:00,2025-01-21 00:00:00"

    Ý nghĩa:
    Đây là thời điểm batch xử lý, không phải giá trị date_hour cần ghi.

    - 2025-01-20 12:00:00
      => làm bẩn date_hour từ 2025-01-20 00:00:00 đến 2025-01-20 11:00:00

    - 2025-01-21 00:00:00
      => làm bẩn date_hour từ 2025-01-20 12:00:00 đến 2025-01-20 23:00:00
    """
    date_hours = set()

    for item in parse_list_arg(value):
        date_hours.add(pd.to_datetime(item))

    return date_hours


def normalize_ratio(value: float) -> float:
    """
    Cho phép nhập:
    --dirty-ratio 0.3  => 30%
    --dirty-ratio 30   => 30%
    --dirty-ratio 1    => 100%
    --dirty-ratio 100  => 100%
    """
    ratio = float(value)

    if ratio > 1:
        ratio = ratio / 100.0

    if ratio < 0 or ratio > 1:
        raise ValueError(
            "--dirty-ratio phải nằm trong [0, 1] hoặc [0, 100]. "
            "Ví dụ: 0.3, 30, 1 hoặc 100."
        )

    return ratio


def parse_args():
    parser = argparse.ArgumentParser()

    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--file")
    source.add_argument("--data-dir")

    parser.add_argument("--table", required=True)
    parser.add_argument("--event-col", default="event_time")

    parser.add_argument(
        "--target-date-hour",
        help=(
            "YYYY-MM-DD HH:00:00. "
            "Nếu truyền vào, chỉ ingest đúng các dòng có date_hour bằng giá trị này. "
            "Tham số này giữ nguyên logic cũ."
        ),
    )

    parser.add_argument("--db-url", default=get_db_url())

    parser.add_argument(
        "--dirty-dates",
        default="",
        help=(
            "Danh sách ngày cần làm bẩn, cách nhau bởi dấu phẩy. "
            "Ví dụ: '2025-01-20,2025-01-21'."
        ),
    )

    parser.add_argument(
        "--dirty-date-hours",
        default="",
        help=(
            "Danh sách thời điểm batch cần làm bẩn. "
            "Ví dụ: '2025-01-20 12:00:00,2025-01-21 00:00:00'. "
            "Nếu nhập 12:00 thì làm bẩn date_hour 00-11 cùng ngày. "
            "Nếu nhập 00:00 thì làm bẩn date_hour 12-23 ngày trước."
        ),
    )

    parser.add_argument(
        "--dirty-ratio",
        type=float,
        default=0.0,
        help=(
            "Tỉ lệ dòng bị làm bẩn trong batch/ngày được chọn. "
            "Ví dụ: 0.3 hoặc 30 là 30 phần trăm. "
            "Dùng 1 hoặc 100 nếu muốn làm bẩn toàn bộ."
        ),
    )

    parser.add_argument(
        "--dirty-seed",
        type=int,
        default=2025,
        help="Seed để việc chọn dòng làm bẩn có thể tái lập."
    )

    args = parser.parse_args()

    args.dirty_ratio = normalize_ratio(args.dirty_ratio)
    args.dirty_dates = parse_dirty_dates(args.dirty_dates)
    args.dirty_date_hours = parse_dirty_date_hours(args.dirty_date_hours)

    if args.dirty_ratio > 0 and not args.dirty_dates and not args.dirty_date_hours:
        raise ValueError(
            "Bạn đã truyền --dirty-ratio > 0 nhưng chưa truyền "
            "--dirty-dates hoặc --dirty-date-hours.\n"
            "Ví dụ:\n"
            "--dirty-date-hours '2025-01-20 12:00:00' --dirty-ratio 1"
        )

    return args


# ============================================================
# File collection
# ============================================================

def collect_files(args) -> List[Path]:
    if args.file:
        return [Path(args.file)]

    path = Path(args.data_dir)
    files = sorted(path.glob("*.parquet"))

    if not files:
        raise Exception("No parquet files found")

    return files


# ============================================================
# date_hour logic - giữ nguyên logic job bình thường
# ============================================================

def compute_date_hour(df, event_col):
    """
    Giữ nguyên logic cũ của bạn.

    date_hour vẫn là giờ sự kiện sau khi làm tròn theo rule:
    - minute >= 45 thì cộng thêm 1 giờ
    - sau đó floor về đầu giờ

    Ví dụ:
    10:30 => 10:00
    10:45 => 11:00
    """
    df[event_col] = pd.to_datetime(df[event_col])

    add_hour = (df[event_col].dt.minute >= 45).astype(int)
    processing_time = df[event_col] + pd.to_timedelta(add_hour, unit="h")
    df["date_hour"] = processing_time.dt.floor("h")

    return df


# ============================================================
# Dirty data logic
# ============================================================

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
    """
    Mapping dirty-date-hours theo batch xử lý.

    Lưu ý:
    - Không thay đổi giá trị date_hour được ghi vào PostgreSQL.
    - Chỉ dùng dirty-date-hours để xác định vùng dữ liệu cần làm bẩn.

    Quy ước:

    1. Nếu dirty-date-hours là YYYY-MM-DD 12:00:00
       => làm bẩn date_hour từ YYYY-MM-DD 00:00:00 đến YYYY-MM-DD 11:00:00

    2. Nếu dirty-date-hours là YYYY-MM-DD 00:00:00
       => làm bẩn date_hour từ ngày trước 12:00:00 đến ngày trước 23:00:00
    """
    mask = pd.Series(False, index=date_hour.index)

    for batch_time in dirty_date_hours:
        batch_time = pd.to_datetime(batch_time)

        if batch_time.minute != 0 or batch_time.second != 0:
            raise ValueError(
                f"--dirty-date-hours chỉ nên nhập đúng đầu giờ. "
                f"Giá trị không hợp lệ: {batch_time}"
            )

        if batch_time.hour == 12:
            start_time = batch_time.normalize()
            end_time = batch_time

        elif batch_time.hour == 0:
            end_time = batch_time
            start_time = batch_time - pd.Timedelta(hours=12)

        else:
            raise ValueError(
                f"--dirty-date-hours chỉ hỗ trợ batch 00:00 hoặc 12:00. "
                f"Giá trị không hợp lệ: {batch_time}"
            )

        mask |= (date_hour >= start_time) & (date_hour < end_time)

    return mask


def inject_dirty_data_pandas(
    df: pd.DataFrame,
    dirty_dates: Set[pd.Timestamp],
    dirty_date_hours: Set[pd.Timestamp],
    dirty_ratio: float,
    rng: np.random.Generator,
) -> Tuple[pd.DataFrame, int]:
    """
    Làm bẩn dữ liệu để mô phỏng anomaly.

    Không thêm cột mới để tránh lệch schema khi COPY vào PostgreSQL.

    Các kiểu làm bẩn:
    0. trip_distance tăng bất thường
    1. total_amount tăng bất thường
    2. fare_amount tăng bất thường
    3. store_and_fwd_flag xuất hiện category lạ 'ANOM'
    4. PULocationID/DOLocationID chuyển sang mã bất thường 999
    """
    if dirty_ratio <= 0:
        return df, 0

    if not dirty_dates and not dirty_date_hours:
        return df, 0

    if "date_hour" not in df.columns:
        raise ValueError(
            "Không tìm thấy cột date_hour. "
            "Hãy gọi compute_date_hour() trước khi làm bẩn dữ liệu."
        )

    date_hour = pd.to_datetime(df["date_hour"])

    dirty_mask = pd.Series(False, index=df.index)

    # Làm bẩn theo ngày date_hour trực tiếp.
    if dirty_dates:
        dirty_mask |= date_hour.dt.normalize().isin(dirty_dates)

    # Làm bẩn theo batch xử lý 00:00 / 12:00.
    if dirty_date_hours:
        dirty_mask |= build_dirty_batch_mask(
            date_hour=date_hour,
            dirty_date_hours=dirty_date_hours,
        )

    eligible_idx = df.index[dirty_mask].to_numpy()

    if len(eligible_idx) == 0:
        return df, 0

    n_dirty = int(round(len(eligible_idx) * dirty_ratio))

    if dirty_ratio > 0 and n_dirty == 0:
        n_dirty = 1

    n_dirty = min(n_dirty, len(eligible_idx))

    dirty_idx = rng.choice(
        eligible_idx,
        size=n_dirty,
        replace=False,
    )

    dirty_groups = rng.integers(
        low=0,
        high=5,
        size=n_dirty,
    )

    df = df.copy()

    def selected(group_id: int):
        return dirty_idx[dirty_groups == group_id]

    # 1. Làm bẩn trip_distance
    trip_distance_col = find_col_case_insensitive(df, "trip_distance")
    if trip_distance_col is not None:
        idx = selected(0)
        if len(idx) > 0:
            df.loc[idx, trip_distance_col] = (
                pd.to_numeric(df.loc[idx, trip_distance_col], errors="coerce") * 5.0
            )

    # 2. Làm bẩn total_amount
    total_amount_col = find_col_case_insensitive(df, "total_amount")
    if total_amount_col is not None:
        idx = selected(1)
        if len(idx) > 0:
            df.loc[idx, total_amount_col] = (
                pd.to_numeric(df.loc[idx, total_amount_col], errors="coerce") * 4.0
            )

    # 3. Làm bẩn fare_amount
    fare_amount_col = find_col_case_insensitive(df, "fare_amount")
    if fare_amount_col is not None:
        idx = selected(2)
        if len(idx) > 0:
            df.loc[idx, fare_amount_col] = (
                pd.to_numeric(df.loc[idx, fare_amount_col], errors="coerce") * 4.0
            )

    # 4. Làm bẩn categorical flag
    store_flag_col = find_col_case_insensitive(df, "store_and_fwd_flag")
    if store_flag_col is not None:
        idx = selected(3)
        if len(idx) > 0:
            df.loc[idx, store_flag_col] = "X"

    # 5. Làm bẩn location ID
    idx = selected(4)
    if len(idx) > 0:
        pu_location_col = find_col_case_insensitive(df, "PULocationID")
        do_location_col = find_col_case_insensitive(df, "DOLocationID")

        if pu_location_col is not None:
            df.loc[idx, pu_location_col] = 999

        if do_location_col is not None:
            df.loc[idx, do_location_col] = 999

    return df, n_dirty


# ============================================================
# Processing
# ============================================================

def process_file(
    file_path,
    db_url,
    table,
    event_col,
    target_date_hour,
    dirty_dates,
    dirty_date_hours,
    dirty_ratio,
    dirty_seed,
):
    print(f"[PROCESS] {file_path} | target_date_hour={target_date_hour}")

    if dirty_ratio > 0:
        print(
            "[DIRTY CONFIG] "
            f"dirty_dates={sorted([str(x.date()) for x in dirty_dates])} | "
            f"dirty_date_hours={sorted([str(x) for x in dirty_date_hours])} | "
            f"dirty_ratio={dirty_ratio:.4f} | "
            f"dirty_seed={dirty_seed}"
        )

    parquet_file = pq.ParquetFile(file_path)
    total_rows = parquet_file.metadata.num_rows

    inserted = 0
    dirtied = 0

    target_dt = pd.to_datetime(target_date_hour) if target_date_hour else None
    rng = np.random.default_rng(int(dirty_seed))

    with tqdm(total=total_rows) as pbar:
        for batch in parquet_file.iter_batches(batch_size=100000):
            df = batch.to_pandas()
            raw_len = len(df)

            if df.empty:
                pbar.update(raw_len)
                continue

            df = compute_date_hour(df, event_col)

            # Giữ nguyên logic cũ:
            # Nếu target_date_hour được truyền, chỉ ingest đúng date_hour đó.
            if target_dt is not None:
                df = df[df["date_hour"] == target_dt]

            if df.empty:
                pbar.update(raw_len)
                continue

            df, dirty_count = inject_dirty_data_pandas(
                df=df,
                dirty_dates=dirty_dates,
                dirty_date_hours=dirty_date_hours,
                dirty_ratio=dirty_ratio,
                rng=rng,
            )

            copy_to_postgres(df, db_url, table)

            inserted += len(df)
            dirtied += dirty_count

            pbar.update(raw_len)

    print(f"[DONE] inserted={inserted} | dirtied={dirtied}")

    return inserted, dirtied


def main():
    args = parse_args()

    files = collect_files(args)

    total_inserted = 0
    total_dirtied = 0
    start = time.time()

    for f in files:
        inserted, dirtied = process_file(
            file_path=f,
            db_url=args.db_url,
            table=args.table,
            event_col=args.event_col,
            target_date_hour=args.target_date_hour,
            dirty_dates=args.dirty_dates,
            dirty_date_hours=args.dirty_date_hours,
            dirty_ratio=args.dirty_ratio,
            dirty_seed=args.dirty_seed,
        )

        total_inserted += inserted
        total_dirtied += dirtied

    print("\n=======================")
    print(f"Total inserted: {total_inserted}")
    print(f"Total dirtied: {total_dirtied}")
    print(f"Time: {time.time() - start:.2f}s")
    print("=======================")


if __name__ == "__main__":
    main()