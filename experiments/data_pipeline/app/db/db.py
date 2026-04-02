import time
import psycopg2
from psycopg2.extensions import connection as PgConnection

from config import config

_MAX_RETRIES = 3
_RETRY_DELAY = 5 


def get_connection() -> PgConnection:
    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            print(f"Connecting to Postgres (attempt {attempt})...")
            conn = psycopg2.connect(
                host=config.POSTGRES_HOST,
                port=config.POSTGRES_PORT,
                dbname=config.POSTGRES_DB,
                user=config.POSTGRES_USER,
                password=config.POSTGRES_PASSWORD,
                connect_timeout=10,
            )
            return conn
        except psycopg2.OperationalError as e:
            print(f"Connection failed: {e}")
            if attempt < _MAX_RETRIES:
                time.sleep(_RETRY_DELAY)
            else:
                raise
