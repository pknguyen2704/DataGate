import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "DataGate"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "7b68832a8a815a51357635c91178659139268383dfa32e825000")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://admin:datagatepassword@localhost:5432/datagate")

    # Airflow
    AIRFLOW_URL: str = os.getenv("AIRFLOW_URL", "http://localhost:8089")
    AIRFLOW_USER: str = os.getenv("AIRFLOW_USER", "airflow")
    AIRFLOW_PASS: str = os.getenv("AIRFLOW_PASS", "airflow")

    class Config:
        case_sensitive = True

settings = Settings()
