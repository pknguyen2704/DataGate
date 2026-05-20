import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parents[2] / ".env")


def _get_env(*keys: str, default: str | None = None) -> str:
    for key in keys:
        value = os.getenv(key)
        if value is not None and value.strip() != "":
            return value.strip()

    if default is not None and default.strip() != "":
        return default.strip()

    names = ", ".join(keys)
    raise RuntimeError(f"Missing required environment variable: {names}")


def _get_int_env(*keys: str, default: int | None = None) -> int:
    value = _get_env(*keys, default=str(default) if default is not None else None)
    return int(value)


def _strip_url(value: str) -> str:
    return value.rstrip("/")


def _build_database_url() -> str:
    user = _get_env("POSTGRES_USER", "DATABASE_USER")
    password = _get_env("POSTGRES_PASSWORD", "DATABASE_PASSWORD")
    host = _get_env("DATABASE_HOST", default="localhost")
    port = _get_env("DATABASE_PORT", default="5432")
    db = _get_env("POSTGRES_DB", "DATABASE_DB")
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"


class Config:
    app_name: str = _get_env("APP_NAME", default="DataGate")
    app_version: str = _get_env("APP_VERSION", default="1.0.0")
    api_v1_str: str = _get_env("API_V1_STR", default="/api/v1")
    tz: str = _get_env("TZ", default="Asia/Ho_Chi_Minh")

    secret_key: str = _get_env("SECRET_KEY")
    algorithm: str = _get_env("ALGORITHM", default="HS256")
    access_token_expire_minutes: int = _get_int_env(
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        default=60,
    )

    database_host: str = _get_env("DATABASE_HOST", default="localhost")
    database_port: int = _get_int_env("DATABASE_PORT", default=5432)
    database_user: str = _get_env("POSTGRES_USER", "DATABASE_USER")
    database_password: str = _get_env("POSTGRES_PASSWORD", "DATABASE_PASSWORD")
    database_db: str = _get_env("POSTGRES_DB", "DATABASE_DB")
    database_url: str = _build_database_url()

    grafana_admin_user: str = _get_env("GF_SECURITY_ADMIN_USER", default="admin")
    grafana_admin_password: str = _get_env(
        "GF_SECURITY_ADMIN_PASSWORD",
        default="grafanapassword",
    )
    grafana_url: str = _strip_url(
        _get_env("GRAFANA_URL", default="http://localhost:3000")
    )
    grafana_dashboard_uid: str = _get_env("GRAFANA_DASHBOARD_UID", default="ads54vs")
    grafana_dashboard_slug: str = _strip_url(
        _get_env(
            "GRAFANA_DASHBOARD_SLUG",
            default="table-metadata-and-profiling-per-batch",
        )
    )

    notebook_url: str = _strip_url(
        _get_env("NOTEBOOK_URL", default="http://localhost:8888/lab")
    )
    notebook_token: str = _get_env(
        "JUPYTER_TOKEN",
        default="dev-token",
    )


config = Config()
