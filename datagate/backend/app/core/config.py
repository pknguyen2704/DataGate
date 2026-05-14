import os
from dotenv import load_dotenv

load_dotenv()

def _get_env(key: str, default: str | None = None) -> str:
    value = os.getenv(key, default)
    if value is None or value.strip() == "":
        raise RuntimeError(f"Missing required environment variable: {key}")
    return value.strip()

def _get_int_env(key: str, default: int | None = None) -> int:
    value = os.getenv(key)
    if value is None or value.strip() == "":
        if default is not None:
            return default
        raise RuntimeError(f"Missing required environment variable: {key}")
    return int(value)

def _build_database_url() -> str:
    user = _get_env("DATABASE_USER")
    password = _get_env("DATABASE_PASSWORD")
    host = _get_env("DATABASE_HOST")
    port = _get_env("DATABASE_PORT")
    db = _get_env("DATABASE_DB")

    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"


class Config:
    app_name: str = _get_env("APP_NAME", "DataGate")
    app_version: str = _get_env("APP_VERSION", "1.0.0")
    api_v1_str: str = _get_env("API_V1_STR", "/api/v1")
    tz: str = _get_env("TZ", "Asia/Ho_Chi_Minh")

    secret_key: str = _get_env("SECRET_KEY")
    algorithm: str = _get_env("ALGORITHM", "HS256")
    access_token_expire_minutes: int = _get_int_env(
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        default=60,
    )

    database_host: str = _get_env("DATABASE_HOST")
    database_port: int = _get_int_env("DATABASE_PORT")
    database_user: str = _get_env("DATABASE_USER")
    database_password: str = _get_env("DATABASE_PASSWORD")
    database_db: str = _get_env("DATABASE_DB")
    database_url: str = _build_database_url()
    
    grafana_url: str = _get_env("GRAFANA_URL", "http://datagate.io.vn:3000").strip("/")
    grafana_dashboard_uid: str = _get_env("GRAFANA_DASHBOARD_UID", "adcx6gp")
    grafana_dashboard_slug: str = _get_env(
        "GRAFANA_DASHBOARD_SLUG",
        "table-metadata-and-profiling-per-batch",
    ).strip("/")

config = Config()
