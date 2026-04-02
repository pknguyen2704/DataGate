"""
extract.py
──────────
Read raw rows from the yellow_tripdata table in PostgreSQL.
Cursor is based on TIMESTAMP column: lpep_dropoff_datetime.
"""

from psycopg2.extensions import connection as PgConnection

from config import config


def fetch_batch(conn: PgConnection, last_timestamp: str) -> list[dict]:
    """
    Fetch up to BATCH_SIZE rows where lpep_dropoff_datetime > last_timestamp,
    ordered by timestamp ASC so records are always processed in chronological order.

    Returns a list of dicts.
    """
    query = f"""
        SELECT *
        FROM {config.SOURCE_TABLE}
        WHERE tpep_dropoff_datetime > %(last_timestamp)s
        ORDER BY tpep_dropoff_datetime ASC
        LIMIT %(batch_size)s
    """
    params = {"last_timestamp": last_timestamp, "batch_size": config.BATCH_SIZE}

    with conn.cursor() as cur:
        cur.execute(query, params)
        columns = [desc[0] for desc in cur.description]
        rows = [dict(zip(columns, row)) for row in cur.fetchall()]

    return rows
