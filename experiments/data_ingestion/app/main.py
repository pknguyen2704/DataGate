import sys

from src.logger import setup_logging, get_logger
from src import checkpoint, config
from src.scheduler import start_scheduler
from src.etl_job import run_etl_job

# Log setup
setup_logging()
logger = get_logger(__name__)


def main():
    connection_detail = f"""
    Source:
        - Host: {config.POSTGRES_HOST}
        - Port: {config.POSTGRES_PORT}
        - Database: {config.POSTGRES_DB}
        - Table: {config.SOURCE_TABLE}
    Destination:
        - MinIO: {config.MINIO_ENDPOINT}
        - Bucket: {config.MINIO_BUCKET}
        - Iceberg: {config.ICEBERG_REST_URI}
        - Table: {config.TARGET_TABLE}
    """

    print(connection_detail)

    checkpoint.init_checkpoint_db()

    logger.info("[ETL Service] Starting…")

    try:
        start_scheduler(run_etl_job)
    except KeyboardInterrupt:
        logger.info("[ETL Service] Stopped by user.")
        sys.exit(0)


if __name__ == "__main__":
    main()
