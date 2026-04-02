import os
import sqlite3

from config import config

# Using a very old timestamp as the default start point to ensure all historical data is picked up
DEFAULT_START = "1900-01-01 00:00:00"


def _db_path() -> str:
    return os.path.join(config.CHECKPOINT_DIR, config.CHECKPOINT_DB_NAME)


def init() -> None:
    os.makedirs(config.CHECKPOINT_DIR, exist_ok=True)
    path = _db_path()
    with sqlite3.connect(path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS checkpoint (
                id              INTEGER PRIMARY KEY,
                last_timestamp  TEXT NOT NULL,
                updated_at      TEXT NOT NULL
            )
        """)
        # Insert initial starting point if table is empty
        conn.execute("""
            INSERT OR IGNORE INTO checkpoint (id, last_timestamp, updated_at)
            VALUES (1, ?, datetime('now'))
        """, (DEFAULT_START,))
        conn.commit()


def read() -> dict:
    with sqlite3.connect(_db_path()) as conn:
        row = conn.execute(
            "SELECT last_timestamp FROM checkpoint WHERE id = 1"
        ).fetchone()
    # Default to DEFAULT_START if not found in db
    return {"last_timestamp": row[0] if row else DEFAULT_START}


def save(last_timestamp: str) -> None:
    with sqlite3.connect(_db_path()) as conn:
        conn.execute("""
            UPDATE checkpoint
            SET last_timestamp = ?, updated_at = datetime('now')
            WHERE id = 1
        """, (str(last_timestamp),))
        conn.commit()
