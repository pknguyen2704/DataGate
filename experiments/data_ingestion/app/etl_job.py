import traceback
from src import checkpoint
from src.logger import get_logger
from src.db import get_connection
from src.extract import fetch_new_records
from src.transform import transform_batch
from src.csv_writer import write_rejected_csv
from src.lakehouse_writer import write_to_lakehouse, write_rejected_to_lakehouse

logger = get_logger(__name__)


def run_etl_job():
    # ── Connect to PostgreSQL ──────────────────────────────────────────────────
    conn = None
    try:
        conn = get_connection()
    except Exception as e:
        logger.error(f"Can't connect to PostgreSQL: {e}")
        return

    # ── Read checkpoint ────────────────────────────────────────────────────────
    try:
        current_checkpoint = checkpoint.read_checkpoint()
        last_id = current_checkpoint["last_id"]
        last_event_time = current_checkpoint["last_event_time"]
        logger.info(f"Current checkpoint: last_id={last_id}, last_event_time={last_event_time}")
    except Exception as e:
        logger.error(f"Can't read checkpoint: {e}")
        return

    # ── Extract ────────────────────────────────────────────────────────────────
    try:
        raw_records = fetch_new_records(conn, last_id=last_id)
        logger.info(f"Total records fetched: {len(raw_records)}")
    except Exception as e:
        logger.error(f"Error extracting data: {e}")
        traceback.print_exc()
        return
    finally:
        conn.close()

    if not raw_records:
        logger.info("No new records. End of this run.")
        return

    # ── Transform ──────────────────────────────────────────────────────────────
    try:
        valid_records, rejected_records = transform_batch(raw_records)
        logger.info(f"Valid records: {len(valid_records)}")
        logger.info(f"Rejected records: {len(rejected_records)}")
    except Exception as e:
        logger.error(f"Error transforming data: {e}")
        traceback.print_exc()
        return

    # ── Load — rejected records ────────────────────────────────────────────────
    if rejected_records:
        try:
            # Write rejected Parquet to MinIO quarantine prefix
            write_rejected_to_lakehouse(rejected_records)
        except Exception as e:
            # Rejected-write failure must not abort the main load
            logger.error(f"Error writing rejected records to lakehouse (ignored): {e}")

    # ── Load — valid records → lakehouse ──────────────────────────────────────
    if valid_records:
        try:
            s3_uri = write_to_lakehouse(valid_records)
            logger.info(f"Lakehouse output: {s3_uri}")
        except Exception as e:
            logger.error(f"Error writing to lakehouse: {e}")
            traceback.print_exc()
            # DO NOT update checkpoint if the lakehouse write fails
            logger.warning("Checkpoint NOT updated due to lakehouse write error.")
            return

        # ── Update checkpoint ONLY after successful lakehouse write ────────────
        try:
            new_last_id = max(r["id"] for r in valid_records)
            new_last_event_time = max(r["event_time_utc"] for r in valid_records)
            checkpoint.save_checkpoint(new_last_id, new_last_event_time)
        except Exception as e:
            logger.error(f"Error saving checkpoint: {e}")
            return
    else:
        logger.info("No valid records to write to lakehouse.")

    # ── Summary ────────────────────────────────────────────────────────────────
    logger.info("─" * 60)
    logger.info("ETL RUN RESULT:")
    logger.info(f"Previous checkpoint : last_id={last_id}")
    logger.info(f"Total records       : {len(raw_records)}")
    logger.info(f"Valid records       : {len(valid_records)}")
    logger.info(f"Rejected records    : {len(rejected_records)}")
    if valid_records:
        logger.info(f"New checkpoint      : last_id={max(r['id'] for r in valid_records)}")
    logger.info("=" * 60)
