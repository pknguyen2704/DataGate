#!/usr/bin/env python3
import argparse
import os
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text

def main():
    parser = argparse.ArgumentParser(description="Upload Parquet files to PostgreSQL.")
    
    # Input source options
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--data-dir", help="Directory containing Parquet files")
    group.add_argument("--file", dest="files", action="append", help="Specific file(s) to upload. Can be used multiple times.")
    
    parser.add_argument("--pattern", default="*.parquet", help="File pattern to match (only used with --data-dir)")
    parser.add_argument("--db-url", default="postgresql://admin:postgrepassword@localhost:54321/postgres", help="Database connection string")
    parser.add_argument("--table", help="Target table name. If set, all files merge into this table.")
    parser.add_argument("--table-prefix", default="tlc_data_", help="Prefix for table names (only used if --table is NOT set)")
    parser.add_argument("--mode", choices=["replace", "append"], default="append", help="Upload mode. 'replace' overwrites the table; 'append' adds to it.")
    
    args = parser.parse_args()

    # Collect files
    file_paths = []
    if args.data_dir:
        data_dir = Path(args.data_dir).resolve()
        if not data_dir.exists():
            print(f"Error: Directory {data_dir} does not exist.")
            return
        file_paths = sorted(data_dir.glob(args.pattern))
        if not file_paths:
            print(f"No files found matching {args.pattern} in {data_dir}")
            return
    elif args.files:
        for f in args.files:
            p = Path(f).resolve()
            if not p.exists():
                print(f"Error: File {p} does not exist.")
                return
            file_paths.append(p)
    
    # Connect
    print(f"Connecting to database...")
    try:
        engine = create_engine(args.db_url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Database connection successful.")
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        return

    # Processing
    # If using a single target table with 'replace' mode, we only 'replace' on the FIRST file,
    # then 'append' for the rest.
    current_mode = args.mode
    
    for i, file_path in enumerate(file_paths):
        # Determine target table name
        if args.table:
            table_name = args.table
            
            # Smart handling for bulk upload to single table
            if args.mode == "replace":
                if i == 0:
                    current_mode = "replace"
                else:
                    current_mode = "append" # Force append for subsequent files
            else:
                current_mode = "append"
        else:
            # Derived table name
            clean_name = file_path.stem.replace("-", "_").replace(".", "_")
            table_name = f"{args.table_prefix}{clean_name}"
            current_mode = args.mode # Reset to user choice for every file

        print(f"Processing {file_path.name} -> Table: {table_name} (mode: {current_mode})")
        
        try:
            df = pd.read_parquet(file_path)
            # Normalize columns
            df.columns = [c.lower() for c in df.columns]
            
            df.to_sql(table_name, engine, if_exists=current_mode, index=False, chunksize=10000)
            print(f"  [OK] Uploaded {len(df)} rows.")
        except Exception as e:
            print(f"  [ERR] Failed uploading {file_path.name}: {e}")

if __name__ == "__main__":
    import time
    start_time = time.time()
    try:
        main()
    finally:
        print(f"Total execution time: {time.time() - start_time:.2f} seconds")
