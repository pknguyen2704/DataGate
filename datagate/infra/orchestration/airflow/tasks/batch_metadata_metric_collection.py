import logging
import uuid
from contextlib import suppress
from datetime import datetime
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.trino.hooks.trino import TrinoHook
from psycopg2.extras import execute_values

# Log
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Validation
def validate_name(value, field_name):
    if value is None or str(value).strip() == "":
        raise ValueError(f"{field_name} must not be None or empty.")
    value = str(value).strip()
    for char in value:
        if not (char.isalnum() or char == "_" or char == " "):
            raise ValueError(f"Invalid {field_name}: {value}.")
    return value

# Normalize processing date hour
def normalize_processing_date_hour(processing_date_hour):
    if processing_date_hour is None:
        raise ValueError("processing_date_hour must not be None or empty.")
    value = str(processing_date_hour).strip().replace("T", " ")
    if value == "":
        raise ValueError("processing_date_hour must not be empty.")
    dt = datetime.fromisoformat(value)
    return dt.strftime("%Y-%m-%d %H:%M:%S")

# Get connection_config from Datagate database
def get_connection_config(pg_hook, connection_name):
    if connection_name is None or str(connection_name).strip() == "":
        raise ValueError("connection_name must not be None or empty.")
    connection_name = str(connection_name).strip()
    row = pg_hook.get_first(
        """
        SELECT
            id,
            catalog_name
        FROM connections
        WHERE connection_name = %s
          AND is_active = TRUE
        LIMIT 1
        """,
        parameters=(connection_name,)
    )
    if row is None:
        raise ValueError(f"No active connection found with connection_name={connection_name}")
    connection_id = str(row[0])
    catalog_name = validate_name(row[1], "catalog_name")

    return {
        "connection_id": connection_id,
        "catalog_name": catalog_name
    }

# Get active tables from Datagate database
def get_active_tables(pg_hook, connection_id, catalog_name, schema_name):
    rows = pg_hook.get_records(
        """
        SELECT
            id,
            table_name
        FROM tables
        WHERE connection_id = %s
          AND catalog_name = %s
          AND schema_name = %s
          AND is_active = TRUE
        ORDER BY table_name
        """,
        parameters=(connection_id, catalog_name, schema_name)
    )

    tables = []

    for table_id, table_name in rows:
        table_name = validate_name(table_name, "table_name")

        tables.append(
            {
                "table_id": str(table_id),
                "table_name": table_name,
                "full_table_name": f"{catalog_name}.{schema_name}.{table_name}",
            }
        )

    return tables


def fetch_one_as_dict(query_engine_hook, sql):
    cursor = query_engine_hook.get_cursor()
    try:
        cursor.execute(sql)
        row = cursor.fetchone()
        if row is None:
            return None
        columns = [desc[0] for desc in cursor.description]
        return dict(zip(columns, row))
    finally:
        with suppress(Exception):
            cursor.close()

# Build SQL query to get batch table metadata
def build_batch_table_metadata_sql(catalog_name, schema_name, table_name, processing_date_hour):
    snapshots_table = f'{catalog_name}.{schema_name}."{table_name}$snapshots"'

    return f"""
    WITH target_snapshot AS (
        SELECT summary
        FROM {snapshots_table}
        ORDER BY committed_at DESC
        LIMIT 1
    )
    SELECT
        COALESCE(
            TRY_CAST(element_at(summary, 'added-records') AS BIGINT),
            0
        ) AS batch_added_rows,

        COALESCE(
            TRY_CAST(element_at(summary, 'added-data-files') AS INTEGER),
            TRY_CAST(element_at(summary, 'added-files') AS INTEGER),
            0
        ) AS batch_added_files,

        COALESCE(
            TRY_CAST(element_at(summary, 'added-files-size') AS BIGINT),
            0
        ) AS batch_added_files_size_bytes,

        COALESCE(
            TRY_CAST(element_at(summary, 'total-records') AS BIGINT),
            0
        ) AS table_total_rows,

        COALESCE(
            TRY_CAST(element_at(summary, 'total-data-files') AS INTEGER),
            TRY_CAST(element_at(summary, 'total-files') AS INTEGER),
            0
        ) AS table_total_files,

        COALESCE(
            TRY_CAST(element_at(summary, 'total-files-size') AS BIGINT),
            0
        ) AS table_total_size_bytes,

        TIMESTAMP '{processing_date_hour}' AS processing_date_hour
    FROM target_snapshot
    """

# Upsert batch table metadata to Datagate database
def save_batch_table_metadata(pg_hook, table_id, metadata):
    sql = """
        INSERT INTO batch_table_metadata (
            id, table_id, batch_added_rows, batch_added_files,
            batch_added_files_size_bytes, table_total_rows, table_total_files,
            table_total_size_bytes, processing_date_hour, created_at, updated_at
        )
        VALUES %s
        ON CONFLICT (table_id, processing_date_hour)
        DO UPDATE SET
            batch_added_rows = EXCLUDED.batch_added_rows,
            batch_added_files = EXCLUDED.batch_added_files,
            batch_added_files_size_bytes = EXCLUDED.batch_added_files_size_bytes,
            table_total_rows = EXCLUDED.table_total_rows,
            table_total_files = EXCLUDED.table_total_files,
            table_total_size_bytes = EXCLUDED.table_total_size_bytes,
            updated_at = NOW()
    """
    values = [
        (
            str(uuid.uuid4()),
            table_id,
            metadata.get("batch_added_rows"),
            metadata.get("batch_added_files"),
            metadata.get("batch_added_files_size_bytes"),
            metadata.get("table_total_rows"),
            metadata.get("table_total_files"),
            metadata.get("table_total_size_bytes"),
            metadata["processing_date_hour"]
        )
    ]
    conn = pg_hook.get_conn()
    with conn.cursor() as cursor:
        execute_values(
            cursor,
            sql,
            values,
            template="(%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())"
        )
    conn.commit()

# Collect one table metadata
def collect_one_table_metadata(
    query_engine_hook,
    pg_hook,
    catalog_name,
    schema_name,
    table_info,
    processing_date_hour
):
    table_id = table_info["table_id"]
    table_name = table_info["table_name"]
    sql = build_batch_table_metadata_sql(catalog_name, schema_name, table_name, processing_date_hour)
    metadata = fetch_one_as_dict(query_engine_hook,sql=sql)
    if metadata is None:
        logger.warning(
            "No Iceberg metadata found for table: %s.%s.%s",
            catalog_name,
            schema_name,
            table_name,
        )
        return
    save_batch_table_metadata(pg_hook, table_id, metadata)
    logger.info(
        "Saved batch table metadata | table=%s.%s.%s | table_id=%s | processing_date_hour=%s",
        catalog_name,
        schema_name,
        table_name,
        table_id,
        processing_date_hour
    )

# Close hook connection
def close_hook_connection(hook):
    if hook is None:
        return
    for attr_name in ("conn", "_conn"):
        with suppress(Exception):
            conn = getattr(hook, attr_name, None)
            if conn is not None:
                conn.close()

# Collect metadata
def batch_metadata_metric_collection(
    query_engine_conn_id,
    datagate_db_conn_id,
    connection_name,
    schema_name,
    processing_date_hour
):
    connection_name = validate_name(connection_name, "connection_name")
    schema_name = validate_name(schema_name, "schema_name")
    processing_date_hour = normalize_processing_date_hour(processing_date_hour)
    query_engine_hook = None
    pg_hook = None

    try:
        query_engine_hook = TrinoHook(query_engine_conn_id)
        pg_hook = PostgresHook(postgres_conn_id=datagate_db_conn_id)
        connection_config = get_connection_config(pg_hook, connection_name)
        catalog_name = connection_config["catalog_name"]
        active_tables = get_active_tables(pg_hook, connection_config["connection_id"], catalog_name, schema_name)
        if not active_tables:
            logger.warning(
                "No active tables found for connection=%s, catalog=%s, schema=%s",
                connection_name,
                catalog_name,
                schema_name,
            )
            return
        logger.info(
            "Found %s active table(s) | connection=%s | catalog=%s | schema=%s",
            len(active_tables),
            connection_name,
            catalog_name,
            schema_name,
        )
        for table_info in active_tables:
            collect_one_table_metadata(query_engine_hook, pg_hook, catalog_name, schema_name, table_info, processing_date_hour)

    finally:
        close_hook_connection(query_engine_hook)
        close_hook_connection(pg_hook)
