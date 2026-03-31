import os
from dotenv import load_dotenv

load_dotenv()

def get_env(key: str, default: str = "") -> str:
    return os.environ.get(key, default)


def get_env_int(key: str, default: int = 0) -> int:
    value = os.environ.get(key, str(default))
    try:
        return int(value)
    except ValueError:
        return default

# ─── PostgreSQL (source) ───────────────────────────────────────────────────────
POSTGRES_HOST     = get_env("POSTGRES_HOST", "localhost")
POSTGRES_PORT     = get_env_int("POSTGRES_PORT", 5432)
POSTGRES_DB       = get_env("POSTGRES_DB", "postgres")
POSTGRES_USER     = get_env("POSTGRES_USER", "admin")
POSTGRES_PASSWORD = get_env("POSTGRES_PASSWORD", "postgrespassword")
SOURCE_TABLE      = get_env("SOURCE_TABLE", "public.telecom_cdr")

# ─── Scheduling ───────────────────────────────────────────────────────────────
SCHEDULE_INTERVAL_SECONDS = get_env_int("SCHEDULE_INTERVAL_SECONDS", 10)
BATCH_SIZE                = get_env_int("BATCH_SIZE", 1000)

# ─── Runtime directories ──────────────────────────────────────────────────────
REJECTED_DIR        = get_env("REJECTED_DIR", "auto_loader/rejected")
CHECKPOINT_DIR      = get_env("CHECKPOINT_DIR", "auto_loader/checkpoint")
LOG_DIR             = get_env("LOG_DIR", "auto_loader/logs")
CHECKPOINT_DB_NAME = get_env("CHECKPOINT_DB_NAME", "checkpoint.db")

# ─── MinIO / S3 (lakehouse object storage) ────────────────────────────────────
MINIO_ENDPOINT        = get_env("MINIO_ENDPOINT", "http://localhost:9000")
MINIO_ACCESS_KEY      = get_env("MINIO_ACCESS_KEY", "admin")
MINIO_SECRET_KEY      = get_env("MINIO_SECRET_KEY", "miniopassword")
MINIO_BUCKET          = get_env("MINIO_BUCKET", "lakehouse")
MINIO_BRONZE_PREFIX   = get_env("MINIO_BRONZE_PREFIX", "bronze/telecom_cdr")

# ─── Iceberg REST Catalog ─────────────────────────────────────────────────────
ICEBERG_REST_URI  = get_env("ICEBERG_REST_URI", "http://localhost:8181")
ICEBERG_NAMESPACE = get_env("ICEBERG_NAMESPACE", "bronze")
TARGET_TABLE      = get_env("TARGET_TABLE", "bronze.telecom_cdr")
