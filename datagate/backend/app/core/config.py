import os
from dotenv import load_dotenv

load_dotenv()

def get_env(key: str, default=None):
    return os.getenv(key, default)


# Security
SECRET_KEY = get_env("SECRET_KEY")
ALGORITHM = get_env("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(get_env("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# Database
DATABASE_URL = get_env("DATABASE_URL")

# Airflow
AIRFLOW_URL = get_env("AIRFLOW_URL")
AIRFLOW_USER = get_env("AIRFLOW_USER")
AIRFLOW_PASS = get_env("AIRFLOW_PASS")

# Minio
MINIO_ENDPOINT = get_env("MINIO_ENDPOINT")
MINIO_USER = get_env("MINIO_USER")
MINIO_PASSWORD = get_env("MINIO_PASSWORD")

# Timezone
TZ = get_env("TZ", "Asia/Ho_Chi_Minh")

