import logging
import uuid
from datetime import datetime
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.trino.hooks.trino import TrinoHook

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def validate_name(value, field_name):
    value = str(value or "").strip()
    if not value:
        raise ValueError(f"{field_name} must not be empty.")
    for char in value:
        if not (char.isalnum() or char == "_" or char == " "):
            raise ValueError(f"Invalid {field_name}: {value}.")
    return value

def normalize_processing_date_hour(processing_date_hour):
    if processing_date_hour is None:
        raise ValueError("processing_date_hour must not be None.")
    value = str(processing_date_hour).strip().replace("T", " ")
    if value == "":
        raise ValueError("processing_date_hour must not be empty.")
    dt = datetime.fromisoformat(value)
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def get_connection_config(pg_hook, connection_name):
    if connection_name is None or str(connection_name).strip() == "":
        raise ValueError("connection_name must not be empty.")
    connection_name = str(connection_name).strip()
    row = pg_hook.get_first(
        """
        SELECT
            id,
            connection_name,
            iceberg_catalog_name
        FROM connections
        WHERE connection_name = %s
          AND is_active = TRUE
        LIMIT 1
        """,
        parameters=(connection_name,),
    )
    if row is None:
        raise ValueError(
            f"No active connection found with connection_name={connection_name}"
        )
    connection_id = str(row[0])
    connection_name = str(row[1])
    iceberg_catalog_name = validate_name(
        row[2],
        "iceberg_catalog_name",
    )
    return {
        "connection_id": connection_id,
        "connection_name": connection_name,
        "iceberg_catalog_name": iceberg_catalog_name,
    }

def get_active_tables(pg_hook, catalog_name, schema_name):
    rows = pg_hook.get_records(
        """
        SELECT
            id,
            table_name
        FROM tables
        WHERE catalog_name = %s
          AND schema_name = %s
          AND is_active = TRUE
        ORDER BY table_name
        """,
        parameters=(catalog_name, schema_name),
    )
    tables = []
    for table_id, table_name in rows:
        table_name = validate_name(table_name, "table_name")

        tables.append(
            {
                "table_id": str(table_id),
                "table_name": table_name,
            }
        )
    return tables

def fetch_one_as_dict(trino_hook, sql):
    cursor = trino_hook.get_cursor()
    cursor.execute(sql)
    row = cursor.fetchone()
    if row is None:
        return None
    columns = [desc[0] for desc in cursor.description]
    return dict(zip(columns, row))

def build_batch_table_metadata_sql(
    catalog_name,
    schema_name,
    table_name,
    processing_date_hour,
):
    snapshots_table = f'{catalog_name}.{schema_name}."{table_name}$snapshots"'
    files_table = f'{catalog_name}.{schema_name}."{table_name}$files"'

    return f"""
    WITH latest_snapshot AS (
        SELECT summary
        FROM {snapshots_table}
        ORDER BY committed_at DESC
        LIMIT 1
    ),
    current_table_stats AS (
        SELECT
            COALESCE(SUM(record_count), 0) AS table_total_rows,
            COUNT(*) AS table_total_files,
            COALESCE(SUM(file_size_in_bytes), 0) AS table_total_size_bytes
        FROM {files_table}
    )
    SELECT
        COALESCE(
            TRY_CAST(element_at(s.summary, 'added-records') AS BIGINT),
            0
        ) AS batch_added_rows,

        COALESCE(
            TRY_CAST(element_at(s.summary, 'added-data-files') AS INTEGER),
            TRY_CAST(element_at(s.summary, 'added-files') AS INTEGER),
            0
        ) AS batch_added_files,

        COALESCE(
            TRY_CAST(element_at(s.summary, 'added-files-size') AS BIGINT),
            0
        ) AS batch_added_files_size_bytes,

        CAST(t.table_total_rows AS BIGINT) AS table_total_rows,
        CAST(t.table_total_files AS INTEGER) AS table_total_files,
        CAST(t.table_total_size_bytes AS BIGINT) AS table_total_size_bytes,

        TIMESTAMP '{processing_date_hour}' AS processing_date_hour
    FROM latest_snapshot s
    CROSS JOIN current_table_stats t
    """

def upsert_batch_table_metadata(pg_hook, table_id, metadata):
    pg_hook.run(
        """
        INSERT INTO batch_table_metadata (
            id,
            table_id,
            batch_added_rows,
            batch_added_files,
            batch_added_files_size_bytes,
            table_total_rows,
            table_total_files,
            table_total_size_bytes,
            processing_date_hour,
            created_at,
            updated_at
        )
        VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW()
        )
        ON CONFLICT (table_id, processing_date_hour)
        DO UPDATE SET
            batch_added_rows = EXCLUDED.batch_added_rows,
            batch_added_files = EXCLUDED.batch_added_files,
            batch_added_files_size_bytes = EXCLUDED.batch_added_files_size_bytes,
            table_total_rows = EXCLUDED.table_total_rows,
            table_total_files = EXCLUDED.table_total_files,
            table_total_size_bytes = EXCLUDED.table_total_size_bytes,
            updated_at = NOW()
        """,
        parameters=(
            str(uuid.uuid4()),
            table_id,
            metadata["batch_added_rows"],
            metadata["batch_added_files"],
            metadata["batch_added_files_size_bytes"],
            metadata["table_total_rows"],
            metadata["table_total_files"],
            metadata["table_total_size_bytes"],
            metadata["processing_date_hour"],
        ),
    )

def collect_one_table_metadata(
    trino_hook,
    pg_hook,
    catalog_name,
    schema_name,
    table_info,
    processing_date_hour,
):
    table_id = table_info["table_id"]
    table_name = table_info["table_name"]
    sql = build_batch_table_metadata_sql(
        catalog_name=catalog_name,
        schema_name=schema_name,
        table_name=table_name,
        processing_date_hour=processing_date_hour,
    )
    metadata = fetch_one_as_dict(
        trino_hook=trino_hook,
        sql=sql,
    )
    if metadata is None:
        logger.warning(
            "No Iceberg metadata found for table: %s.%s.%s",
            catalog_name,
            schema_name,
            table_name,
        )
        return
    upsert_batch_table_metadata(
        pg_hook=pg_hook,
        table_id=table_id,
        metadata=metadata,
    )
    logger.info(
        "Saved batch table metadata | table=%s.%s.%s | table_id=%s | processing_date_hour=%s",
        catalog_name,
        schema_name,
        table_name,
        table_id,
        processing_date_hour,
    )

def collect_metadata(
    trino_conn_id,
    datagate_db_conn_id,
    connection_name,
    schema_name,
    processing_date_hour,
):
    schema_name = validate_name(schema_name, "schema_name")
    processing_date_hour = normalize_processing_date_hour(processing_date_hour)
    trino_hook = TrinoHook(trino_conn_id=trino_conn_id)
    pg_hook = PostgresHook(postgres_conn_id=datagate_db_conn_id)
    connection_config = get_connection_config(
        pg_hook=pg_hook,
        connection_name=connection_name,
    )
    catalog_name = connection_config["iceberg_catalog_name"]
    active_tables = get_active_tables(
        pg_hook=pg_hook,
        catalog_name=catalog_name,
        schema_name=schema_name,
    )
    if not active_tables:
        logger.warning(
            "No active tables found for connection=%s, catalog=%s, schema=%s",
            connection_config["connection_name"],
            catalog_name,
            schema_name,
        )
        return
    logger.info(
        "Found %s active table(s) | connection=%s | catalog=%s | schema=%s",
        len(active_tables),
        connection_config["connection_name"],
        catalog_name,
        schema_name,
    )
    for table_info in active_tables:
        collect_one_table_metadata(
            trino_hook=trino_hook,
            pg_hook=pg_hook,
            catalog_name=catalog_name,
            schema_name=schema_name,
            table_info=table_info,
            processing_date_hour=processing_date_hour,
        )