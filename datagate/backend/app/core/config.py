import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str
    API_V1_STR: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    
    # Database
    DATABASE_URL: str

    # Airflow
    AIRFLOW_URL: str
    AIRFLOW_USER: str
    AIRFLOW_PASS: str

    class Config:
        case_sensitive = True

settings = Settings()
