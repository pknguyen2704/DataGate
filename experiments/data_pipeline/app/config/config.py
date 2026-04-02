import os
from dotenv import load_dotenv

load_dotenv()


def get_env(key: str, default: str = "") -> str:
    return os.environ.get(key, str(default))


# ─── PostgreSQL (source) ──────────────────
POSTGRES_HOST     = get_env("POSTGRES_HOST", "localhost")
POSTGRES_PORT     = get_env("POSTGRES_PORT", 5432)
POSTGRES_DB       = get_env("POSTGRES_DB", "postgres")
POSTGRES_USER     = get_env("POSTGRES_USER", "admin")
POSTGRES_PASSWORD = get_env("POSTGRES_PASSWORD", "postgrespassword")
SOURCE_TABLE      = get_env("SOURCE_TABLE", "public.yellow_tripdata")

# ─── Scheduling & Batch ───────────────────
SCHEDULE_INTERVAL_SECONDS = int(get_env("SCHEDULE_INTERVAL_SECONDS", 30))
BATCH_SIZE                = int(get_env("BATCH_SIZE", 50000))

# ─── MinIO (Medallion structure inside bucket) ────────────────
MINIO_ENDPOINT      = get_env("MINIO_ENDPOINT", "http://localhost:9000")
MINIO_ACCESS_KEY    = get_env("MINIO_ACCESS_KEY", "admin")
MINIO_SECRET_KEY    = get_env("MINIO_SECRET_KEY", "miniopassword")
MINIO_BUCKET        = get_env("MINIO_BUCKET", "lakehouse")

# ─── Iceberg REST Catalog ───────────────
ICEBERG_REST_URI  = get_env("ICEBERG_REST_URI", "http://localhost:8181")
ICEBERG_NAMESPACE = get_env("ICEBERG_NAMESPACE", "bronze")
TARGET_TABLE      = get_env("TARGET_TABLE", "bronze.yellow_tripdata")

# ─── Checkpoint (SQLite) ─────────────────
CHECKPOINT_DIR     = get_env("CHECKPOINT_DIR", "auto_loader/checkpoint")
CHECKPOINT_DB_NAME = get_env("CHECKPOINT_DB_NAME", "checkpoint.db")
