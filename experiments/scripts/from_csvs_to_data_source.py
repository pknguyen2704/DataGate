import argparse
import io
import os
import time
from pathlib import Path
from typing import List
from urllib.parse import urlparse

import pandas as pd
import psycopg2
from dotenv import load_dotenv
from tqdm import tqdm


CITI_BIKE_COLUMNS = [
    "ride_id",
    "rideable_type",
    "started_at",
    "ended_at",
    "start_station_name",
    "start_station_id",
    "end_station_name",
    "end_station_id",
    "start_lat",
    "start_lng",
    "end_lat",
    "end_lng",
    "member_casual",
    "date_hour",
]

DATETIME_COLUMNS = ["started_at", "ended_at"]
NUMERIC_COLUMNS = ["start_lat", "start_lng", "end_lat", "end_lng"]


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


def validate_table_name(table_name):
    parts = table_name.split(".")
    if not 1 <= len(parts) <= 2:
        raise ValueError("table must be table_name or schema.table_name")

    for part in parts:
        if not part or not part.replace("_", "").isalnum():
            raise ValueError(f"Invalid table name: {table_name}")
    return table_name


def parse_args():
    parser = argparse.ArgumentParser()
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--file")
    source.add_argument("--data-dir")
    parser.add_argument("--table", default="public.citi_bike_tripdata")
    parser.add_argument("--event-col", default="started_at")
    parser.add_argument("--target-date-hour", help="YYYY-MM-DD HH:00:00")
    parser.add_argument("--db-url", default=get_db_url())
    parser.add_argument("--chunksize", type=int, default=100000)
    return parser.parse_args()


def collect_files(args) -> List[Path]:
    if args.file:
        return [Path(args.file)]

    path = Path(args.data_dir)
    files = sorted(path.glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"No csv files found in {path}")
    return files


def normalize_batch(df, event_col):
    missing = [column for column in CITI_BIKE_COLUMNS[:-1] if column not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    for column in DATETIME_COLUMNS:
        df[column] = pd.to_datetime(df[column], errors="coerce")
    for column in NUMERIC_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    if event_col not in df.columns:
        raise ValueError(f"event-col does not exist: {event_col}")

    event_time = pd.to_datetime(df[event_col], errors="coerce")
    add_hour = (event_time.dt.minute >= 45).astype("int64")
    df["date_hour"] = (event_time + pd.to_timedelta(add_hour, unit="h")).dt.floor("h")

    return df[CITI_BIKE_COLUMNS]


def copy_to_postgres(df, conn, table_name):
    buffer = io.StringIO()
    df.to_csv(buffer, index=False, header=False, na_rep="")
    buffer.seek(0)

    columns = ", ".join(CITI_BIKE_COLUMNS)
    with conn.cursor() as cursor:
        cursor.copy_expert(
            f"COPY {table_name} ({columns}) FROM STDIN WITH CSV",
            buffer,
        )
    conn.commit()


def count_data_rows(file_path):
    with file_path.open("rb") as file:
        return max(sum(1 for _ in file) - 1, 0)


def process_file(file_path, conn, table_name, event_col, target_date_hour, chunksize):
    print(f"[PROCESS] {file_path} | target={target_date_hour or 'all'}")
    inserted = 0
    target_dt = pd.to_datetime(target_date_hour) if target_date_hour else None

    with tqdm(total=count_data_rows(file_path)) as pbar:
        for df in pd.read_csv(file_path, chunksize=chunksize, dtype=str):
            raw_count = len(df)
            df = normalize_batch(df, event_col)

            if target_dt is not None:
                df = df[df["date_hour"] == target_dt]

            if not df.empty:
                copy_to_postgres(df, conn, table_name)
                inserted += len(df)

            pbar.update(raw_count)

    print(f"[DONE] inserted={inserted}")
    return inserted


def main():
    args = parse_args()
    table_name = validate_table_name(args.table)
    files = collect_files(args)

    total = 0
    start = time.time()
    conn = psycopg2.connect(**parse_db_url(args.db_url))

    try:
        for file_path in files:
            total += process_file(
                file_path,
                conn,
                table_name,
                args.event_col,
                args.target_date_hour,
                args.chunksize,
            )
    finally:
        conn.close()

    print("\n=======================")
    print(f"Total inserted: {total}")
    print(f"Time: {time.time() - start:.2f}s")
    print("=======================")


if __name__ == "__main__":
    main()
