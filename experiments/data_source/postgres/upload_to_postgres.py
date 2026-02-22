#!/usr/bin/env python3
import argparse
import os
import time
import io
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv


def normalize_cols(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [c.lower() for c in df.columns]
    return df


# -------- DB driver selection (NO top-level hard dependency) --------
def get_db_backend():
    """
    Returns (backend_name, module, sql_module).
    backend_name: "psycopg3" or "psycopg2"
    """
    # Try psycopg3 first
    try:
        import psycopg  # psycopg3
        from psycopg import sql as psql
        # simple sanity: ensure pq wrapper exists by importing pq
        import psycopg.pq  # noqa: F401
        return ("psycopg3", psycopg, psql)
    except Exception:
        pass

    # Fallback psycopg2
    try:
        import psycopg2
        import psycopg2.sql as psql2
        return ("psycopg2", psycopg2, psql2)
    except Exception as e:
        raise ImportError(
            "No working PostgreSQL driver found.\n"
            "Fix options:\n"
            "  1) Recommended (fast + easy): pip install -U psycopg2-binary\n"
            "  2) Or psycopg3 with system libpq:\n"
            "     sudo apt-get update && sudo apt-get install -y libpq5 libpq-dev\n"
            "     pip install -U 'psycopg[binary]' || pip install -U psycopg\n"
            f"\nOriginal error: {e}"
        )


def ensure_table_exists(conn, backend_name: str, sqlmod, table_name: str, df_sample: pd.DataFrame, mode: str):
    col_defs = []
    for col, dtype in df_sample.dtypes.items():
        col_id = sqlmod.Identifier(col)
        if pd.api.types.is_integer_dtype(dtype):
            pg_type = sqlmod.SQL("BIGINT")
        elif pd.api.types.is_float_dtype(dtype):
            pg_type = sqlmod.SQL("DOUBLE PRECISION")
        elif pd.api.types.is_bool_dtype(dtype):
            pg_type = sqlmod.SQL("BOOLEAN")
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            pg_type = sqlmod.SQL("TIMESTAMP")
        else:
            pg_type = sqlmod.SQL("TEXT")
        col_defs.append(sqlmod.SQL(" ").join([col_id, pg_type]))

    tbl = sqlmod.Identifier(table_name)

    cur = conn.cursor()
    try:
        if mode == "replace":
            cur.execute(sqlmod.SQL("DROP TABLE IF EXISTS {}").format(tbl))
        cur.execute(
            sqlmod.SQL("CREATE TABLE IF NOT EXISTS {} ({})").format(
                tbl, sqlmod.SQL(", ").join(col_defs)
            )
        )
        conn.commit()
    finally:
        cur.close()


def copy_chunk(conn, backend_name: str, sqlmod, table_name: str, df_chunk: pd.DataFrame, csv_null: str = r"\N"):
    buf = io.StringIO()
    df_chunk.to_csv(
        buf,
        index=False,
        header=False,
        sep=",",
        na_rep=csv_null,
        lineterminator="\n",
    )
    buf.seek(0)

    cols = [sqlmod.Identifier(c) for c in df_chunk.columns]
    stmt = sqlmod.SQL("COPY {} ({}) FROM STDIN WITH (FORMAT csv, DELIMITER ',', NULL {})").format(
        sqlmod.Identifier(table_name),
        sqlmod.SQL(", ").join(cols),
        sqlmod.Literal(csv_null),
    )

    cur = conn.cursor()
    try:
        if backend_name == "psycopg3":
            # psycopg3 copy protocol
            with cur.copy(stmt) as copy:
                copy.write(buf.getvalue())
        else:
            # psycopg2 copy_expert expects a string query
            cur.copy_expert(stmt.as_string(conn), buf)
        conn.commit()
    finally:
        cur.close()


def connect(db_url: str, backend_name: str, backend_mod):
    if backend_name == "psycopg3":
        return backend_mod.connect(db_url)
    return backend_mod.connect(db_url)


def upload_file_via_copy(
    file_path: Path,
    db_url: str,
    table_name: str,
    mode: str,
    chunk_rows: int,
    csv_null: str,
    verbose: bool,
):
    t0 = time.time()

    if verbose:
        print(f"[{file_path.name}] Reading parquet...")
    df = pd.read_parquet(file_path)
    df = normalize_cols(df)

    total_rows = len(df)
    if total_rows == 0:
        return (file_path.name, table_name, 0, time.time() - t0, "EMPTY")

    backend_name, backend_mod, sqlmod = get_db_backend()
    conn = connect(db_url, backend_name, backend_mod)

    try:
        ensure_table_exists(conn, backend_name, sqlmod, table_name, df.head(100), mode)

        if verbose:
            print(f"[{file_path.name}] Uploading {total_rows} rows -> {table_name} (backend={backend_name}, chunk_rows={chunk_rows})")

        uploaded = 0
        for start in range(0, total_rows, chunk_rows):
            end = min(start + chunk_rows, total_rows)
            chunk = df.iloc[start:end]
            copy_chunk(conn, backend_name, sqlmod, table_name, chunk, csv_null=csv_null)
            uploaded = end
            if verbose:
                pct = int(uploaded / total_rows * 100)
                print(f"[{file_path.name}]  Progress: {pct}% ({uploaded}/{total_rows})")

        return (file_path.name, table_name, total_rows, time.time() - t0, "OK")
    finally:
        try:
            conn.close()
        except Exception:
            pass


def main():
    parser = argparse.ArgumentParser(description="Fast multi-thread Parquet -> PostgreSQL uploader (COPY).")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--data-dir", help="Directory containing Parquet files")
    group.add_argument("--file", dest="files", action="append", help="Specific file(s) to upload. Can be used multiple times.")

    script_dir = Path(__file__).parent.resolve()
    load_dotenv(script_dir / ".env")

    pg_user = os.getenv("POSTGRES_USER", "admin")
    pg_password = os.getenv("POSTGRES_PASSWORD", "postgrepassword")
    pg_db = os.getenv("POSTGRES_DB", "postgres")
    default_db_url = f"postgresql://{pg_user}:{pg_password}@localhost:54321/{pg_db}"

    parser.add_argument("--pattern", default="*.parquet")
    parser.add_argument("--db-url", default=default_db_url)
    parser.add_argument("--table", help="Target table name. If set, all files go into this table.")
    parser.add_argument("--table-prefix", default="tlc_data_")
    parser.add_argument("--mode", choices=["replace", "append"], default="append")

    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--chunk-rows", type=int, default=200_000)
    parser.add_argument("--csv-null", default=r"\N")
    parser.add_argument("--no-verbose", action="store_true")
    args = parser.parse_args()

    verbose = not args.no_verbose

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
    else:
        for f in args.files or []:
            p = Path(f).resolve()
            if not p.exists():
                print(f"Error: File {p} does not exist.")
                return
            file_paths.append(p)

    # quick connection test via SQLAlchemy (optional)
    if verbose:
        print("Connecting to database...")
    try:
        engine = create_engine(args.db_url, pool_pre_ping=True)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        if verbose:
            print("Database connection successful.")
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        return

    tasks = []
    for idx, fp in enumerate(file_paths):
        if args.table:
            table_name = args.table
            mode = "replace" if (args.mode == "replace" and idx == 0) else "append"
        else:
            clean_name = fp.stem.replace("-", "_").replace(".", "_")
            table_name = f"{args.table_prefix}{clean_name}"
            mode = args.mode
        tasks.append((fp, table_name, mode))

    if args.table and args.workers > 2 and verbose:
        print("Note: single target table detected; consider --workers 1-2 for best throughput.")

    t0 = time.time()
    results = []

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = [
            ex.submit(
                upload_file_via_copy,
                fp,
                args.db_url,
                table_name,
                mode,
                args.chunk_rows,
                args.csv_null,
                verbose,
            )
            for (fp, table_name, mode) in tasks
        ]
        for fut in as_completed(futs):
            try:
                results.append(fut.result())
            except Exception as e:
                results.append(("UNKNOWN", "UNKNOWN", 0, 0.0, f"ERR: {e}"))

    ok = [r for r in results if r[4] == "OK"]
    total_rows = sum(r[2] for r in ok)
    total_time = time.time() - t0

    print("\n=== Summary ===")
    for fname, tbl, rows, sec, status in sorted(results, key=lambda x: x[0]):
        print(f"{status:4}  {fname:40} -> {tbl:30}  rows={rows:<10}  time={sec:6.2f}s")
    print(f"\nTotal uploaded rows: {total_rows}")
    print(f"Total execution time: {total_time:.2f} seconds")
    if total_time > 0:
        print(f"Approx throughput: {total_rows/total_time:,.0f} rows/sec")


if __name__ == "__main__":
    main()