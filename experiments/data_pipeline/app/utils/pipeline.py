from checkpoint import checkpoint
from db.db import get_connection
from utils.extract import fetch_batch
from utils.loader import load_to_lakehouse


def pipeline() -> None:
    print("Pipeline iteration starting...")
    try:
        conn = get_connection()
        print("Connected to PostgreSQL successfully.")
    except Exception as e:
        print(f"PostgreSQL connection error: {e}")
        return

    # Use 'last_timestamp' for incremental fetch tracking
    cp = checkpoint.read()
    last_timestamp: str = cp["last_timestamp"]
    print(f"Current checkpoint: {last_timestamp}")

    try:
        print(f"Fetching batch from Postgres after {last_timestamp}...")
        records = fetch_batch(conn, last_timestamp=last_timestamp)
        print(f"Extracted {len(records)} records.")
    except Exception as e:
        print(f"Extraction error: {e}")
        return
    finally:
        conn.close()

    if not records:
        print("No new records found.")
        return

    try:
        print(f"Loading {len(records)} records to lakehouse (MinIO + Iceberg)...")
        load_to_lakehouse(records)
        print("Records successfully loaded to lakehouse.")
    except Exception as e:
        print(f"Loading error: {e}")
        return

    # The new checkpoint is the 'tpep_dropoff_datetime' of the very last record processed
    # This ensures we always move forward in time
    new_last_timestamp = records[-1]["tpep_dropoff_datetime"]
    checkpoint.save(new_last_timestamp)
    print(f"Pipeline iteration complete. New checkpoint: {new_last_timestamp}")
