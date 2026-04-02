import sys

from config import config
from checkpoint import checkpoint
from scheduler.scheduler import start
from utils.pipeline import pipeline


def main() -> None:
    checkpoint.init()

    connection_detail = f"""
    Source:
        - Host: {config.POSTGRES_HOST}
        - Port: {config.POSTGRES_PORT}
        - Database: {config.POSTGRES_DB}
        - Table: {config.SOURCE_TABLE}
    Destination (MinIO):
        - Endpoint: {config.MINIO_ENDPOINT}
        - Bucket: {config.MINIO_BUCKET}
    Destination (Iceberg):
        - REST URI: {config.ICEBERG_REST_URI}
        - Namespace: {config.ICEBERG_NAMESPACE}
        - Target Table: {config.TARGET_TABLE}
    Scheduling:
        - Interval: {config.SCHEDULE_INTERVAL_SECONDS}s
        - Batch Size: {config.BATCH_SIZE}
    """
    print("=" * 60)
    print("PIPELINE STARTING")
    print(connection_detail)
    print("=" * 60)

    try:
        start(pipeline)
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
