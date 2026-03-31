import pandas as pd
import os
import argparse
from dotenv import load_dotenv
from sqlalchemy import create_engine
from pathlib import Path
from typing import List
import time
from tqdm import tqdm
import pyarrow.parquet as pq
import psycopg2
import io
from urllib.parse import urlparse

def parse_db_url(db_url):
    url = urlparse(db_url)
    return {
        "dbname": url.path[1:],
        "user": url.username,
        "password": url.password,
        "host": url.hostname,
        "port": url.port,
    }
def ds_connect() -> str:
    load_dotenv()
    user = os.getenv("POSTGRES_USER", "admin")
    password = os.getenv("POSTGRES_PASSWORD", "postgrespassword")
    db = os.getenv("POSTGRES_DB", "postgres")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "54321")
    
    return f"postgresql://{user}:{password}@{host}:{port}/{db}"

def copy_to_postgres(df, db_url, table_name):
    params = parse_db_url(db_url)
    conn = psycopg2.connect(**params)
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
    
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument("--file")
    source_group.add_argument("--data-dir")
    parser.add_argument("--table", required=True)
    parser.add_argument("--pattern", default="*.parquet")
    parser.add_argument("--db-url", default=ds_connect())
    parser.add_argument("--if-exists", default="append")
    return parser.parse_args()

def collect_files(args: argparse.Namespace) -> List[Path]:
    if args.data_dir:
        data_dir = Path(args.data_dir).resolve()
        if not data_dir.exists():
            raise FileNotFoundError(f"Directory not found: {data_dir}")
        files = sorted(data_dir.glob(args.pattern))
        if not files:
            raise FileNotFoundError(f"No files found matching {args.pattern} in {data_dir}")
        return files
    else:
        return [Path(args.file).resolve()]
    
def upload_file(db_url, file_path: Path, table_name: str, if_exists: str) -> int:
    print(f"[DATAGATE] Reading {file_path}")

    parquet_file = pq.ParquetFile(file_path)
    total_rows = parquet_file.metadata.num_rows

    inserted = 0

    with tqdm(total=total_rows, desc=f"Uploading {file_path.name}") as pbar:
        for i, batch in enumerate(parquet_file.iter_batches(batch_size=100000)):
            df = batch.to_pandas()
            if df.empty:
                continue
            copy_to_postgres(df, db_url, table_name)

            inserted += len(df)
            pbar.update(len(df))

    return inserted

def main() -> None:
    args = parse_args()
    files = collect_files(args)

    db_url = args.db_url or ds_connect()

    table_name = args.table
    rows_count = 0
    start_time = time.time()

    for index, file_path in enumerate(tqdm(files, desc="Processing files")):
        if_exists = args.if_exists

        if index > 0 and if_exists == "replace":
            if_exists = "append"

        rows = upload_file(
            db_url=db_url,
            file_path=file_path,
            table_name=table_name,
            if_exists=if_exists,
        )

        rows_count += rows

    print(f"[DATAGATE] Total rows uploaded: {rows_count} in {time.time() - start_time:.2f} seconds")

if __name__ == "__main__":
    main()