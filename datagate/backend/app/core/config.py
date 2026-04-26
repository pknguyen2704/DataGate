from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "DataGate"
    APP_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False

    # Security
    SECRET_KEY: str = "changeme-very-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Database
    DATABASE_USER: str = "postgres"
    DATABASE_PASSWORD: str = "postgres"
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: str = "5432"
    DATABASE_DB: str = "datagate"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_DB}"
        )

    @property
    def DATABASE_URL_SYNC(self) -> str:
        return (
            f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_DB}"
        )

    # Encryption key for sensitive connection configs
    ENCRYPTION_KEY: Optional[str] = None

    # Airflow
    AIRFLOW_BASE_URL: Optional[str] = "http://localhost:8080"
    AIRFLOW_USERNAME: Optional[str] = "airflow"
    AIRFLOW_PASSWORD: Optional[str] = "airflow"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()