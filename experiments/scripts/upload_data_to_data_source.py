import pandas as pd
import argparse
import time
from pathlib import Path
from typing import List
from tqdm import tqdm
import pyarrow.parquet as pq
import psycopg2
import io
from urllib.parse import urlparse
import os
from dotenv import load_dotenv

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
    return f"postgresql://admin:postgrespassword@localhost:5433/postgres"

def copy_to_postgres(df, db_url, table_name):
    conn = psycopg2.connect(**parse_db_url(db_url))
    cursor = conn.cursor()
    buffer = io.StringIO()
    df.to_csv(buffer, index=False, header=False)
    buffer.seek(0)
    cursor.copy_expert(f"COPY {table_name} FROM STDIN WITH CSV", buffer)
    conn.commit()
    cursor.close()
    conn.close()



def parse_args():
    parser = argparse.ArgumentParser()
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--file")
    source.add_argument("--data-dir")
    parser.add_argument("--table", required=True)
    parser.add_argument("--event-col", default="event_time")
    parser.add_argument("--target-date-hour", help="YYYY-MM-DD HH:00:00")
    parser.add_argument("--db-url", default=get_db_url())

    return parser.parse_args()


def collect_files(args) -> List[Path]:
    if args.file:
        return [Path(args.file)]
    path = Path(args.data_dir)
    files = sorted(path.glob("*.parquet"))
    if not files:
        raise Exception("No parquet files found")
    return files

def compute_date_hour(df, event_col):
    df[event_col] = pd.to_datetime(df[event_col])
    add_hour = (df[event_col].dt.minute >= 45).astype(int)
    processing_time = df[event_col] + pd.to_timedelta(add_hour, unit="h")
    df["date_hour"] = processing_time.dt.floor("h")
    return df

def process_file(file_path, db_url, table, event_col, target_date_hour):
    print(f"[PROCESS] {file_path} | target={target_date_hour}")
    parquet_file = pq.ParquetFile(file_path)
    total = parquet_file.metadata.num_rows

    inserted = 0

    if target_date_hour:
        target_dt = pd.to_datetime(target_date_hour)

    with tqdm(total=total) as pbar:
        for batch in parquet_file.iter_batches(batch_size=100000):
            df = batch.to_pandas()
            if df.empty:
                continue
            df = compute_date_hour(df, event_col)
            if target_date_hour:
                df = df[df["date_hour"] == target_dt]
            if df.empty:
                pbar.update(len(df))
                continue
            copy_to_postgres(df, db_url, table)

            inserted += len(df)
            pbar.update(len(df))

    print(f"[DONE] inserted={inserted}")
    return inserted

def main():
    args = parse_args()
    files = collect_files(args)
    total = 0
    start = time.time()

    for f in files:
        total += process_file(
            f,
            args.db_url,
            args.table,
            args.event_col,
            args.target_date_hour
        )

    print("\n=======================")
    print(f"Total inserted: {total}")
    print(f"Time: {time.time() - start:.2f}s")
    print("=======================")


if __name__ == "__main__":
    main()