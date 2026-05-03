from __future__ import annotations

import logging
import uuid
from typing import Sequence

from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.trino.hooks.trino import TrinoHook


ICEBERG_CATALOG = "iceberg"
DEFAULT_DATAGATE_DB_CONN_ID = "datagate_db_default"

logger = logging.getLogger(__name__)


def split_table_name(full_table_name: str) -> tuple[str, str]:
    parts = full_table_name.split(".", 1)

    if len(parts) != 2:
        raise ValueError(
            f"Invalid table name: {full_table_name}. "
            "Expected format: <schema_name>.<table_name>"
        )

    schema_name, table_name = parts
    return schema_name, table_name


def fetch_all_as_dicts(hook: TrinoHook, sql: str) -> list[dict]:
    cursor = hook.get_cursor()
    cursor.execute(sql)

    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()

    return [dict(zip(columns, row)) for row in rows]


def build_table_metadata_sql(full_table_name: str, date_hour: str) -> str:
    schema_name, table_name = split_table_name(full_table_name)

    return f"""
    WITH latest_snapshot AS (
        SELECT
            committed_at,
            snapshot_id,
            parent_id,
            operation,
            summary
        FROM {ICEBERG_CATALOG}.{schema_name}."{table_name}$snapshots"
        ORDER BY committed_at DESC
        LIMIT 1
    ),

    latest_metadata AS (
        SELECT
            latest_snapshot_id,
            latest_schema_id,
            latest_sequence_number,
            timestamp AS metadata_recorded_at
        FROM {ICEBERG_CATALOG}.{schema_name}."{table_name}$metadata_log_entries"
        ORDER BY timestamp DESC
        LIMIT 1
    )

    SELECT
        TIMESTAMP '{date_hour}' AS date_hour,
        '{ICEBERG_CATALOG}' AS catalog_name,
        '{schema_name}' AS schema_name,
        '{table_name}' AS table_name,

        CAST(s.snapshot_id AS VARCHAR) AS snapshot_id,
        CAST(s.parent_id AS VARCHAR) AS parent_snapshot_id,
        s.operation,
        s.committed_at AS last_updated_time,

        COALESCE(TRY_CAST(element_at(s.summary, 'added-records') AS BIGINT), 0) AS batch_added_rows,
        COALESCE(
            TRY_CAST(element_at(s.summary, 'added-data-files') AS INTEGER),
            TRY_CAST(element_at(s.summary, 'added-files') AS INTEGER),
            0
        ) AS batch_added_files,
        COALESCE(TRY_CAST(element_at(s.summary, 'deleted-records') AS BIGINT), 0) AS deleted_rows,
        COALESCE(
            TRY_CAST(element_at(s.summary, 'deleted-data-files') AS INTEGER),
            TRY_CAST(element_at(s.summary, 'deleted-files') AS INTEGER),
            0
        ) AS deleted_files,

        TRY_CAST(element_at(s.summary, 'total-records') AS BIGINT) AS table_total_rows,
        TRY_CAST(element_at(s.summary, 'total-data-files') AS INTEGER) AS table_total_files,
        TRY_CAST(element_at(s.summary, 'total-files-size') AS BIGINT) AS table_total_size_bytes,
        COALESCE(TRY_CAST(element_at(s.summary, 'changed-partition-count') AS INTEGER), 0)
            AS changed_partition_count,

        m.latest_schema_id AS schema_id,
        m.latest_sequence_number,
        m.metadata_recorded_at,
        current_timestamp AS collected_at
    FROM latest_snapshot s
    LEFT JOIN latest_metadata m
        ON m.latest_snapshot_id = s.snapshot_id
    """


def get_table_id(
    pg_hook: PostgresHook,
    catalog_name: str,
    schema_name: str,
    table_name: str,
) -> str | None:
    row = pg_hook.get_first(
        """
        SELECT id
        FROM tables
        WHERE catalog_name = %s
          AND schema_name = %s
          AND table_name = %s
          AND is_active = TRUE
        LIMIT 1
        """,
        parameters=(catalog_name, schema_name, table_name),
    )
    return row[0] if row else None


def upsert_table_metadata(pg_hook: PostgresHook, table_id: str, row: dict) -> None:
    pg_hook.run(
        """
        INSERT INTO table_batch_metadata (
            id,
            table_id,
            catalog_name,
            schema_name,
            table_name,
            snapshot_id,
            parent_snapshot_id,
            operation,
            last_updated_time,
            batch_added_rows,
            batch_added_files,
            deleted_rows,
            deleted_files,
            table_total_rows,
            table_total_files,
            table_total_size_bytes,
            changed_partition_count,
            schema_id,
            latest_sequence_number,
            metadata_recorded_at,
            collected_at
        )
        VALUES (
            %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (table_id, snapshot_id)
        DO UPDATE SET
            parent_snapshot_id = EXCLUDED.parent_snapshot_id,
            operation = EXCLUDED.operation,
            last_updated_time = EXCLUDED.last_updated_time,
            batch_added_rows = EXCLUDED.batch_added_rows,
            batch_added_files = EXCLUDED.batch_added_files,
            deleted_rows = EXCLUDED.deleted_rows,
            deleted_files = EXCLUDED.deleted_files,
            table_total_rows = EXCLUDED.table_total_rows,
            table_total_files = EXCLUDED.table_total_files,
            table_total_size_bytes = EXCLUDED.table_total_size_bytes,
            changed_partition_count = EXCLUDED.changed_partition_count,
            schema_id = EXCLUDED.schema_id,
            latest_sequence_number = EXCLUDED.latest_sequence_number,
            metadata_recorded_at = EXCLUDED.metadata_recorded_at,
            collected_at = EXCLUDED.collected_at
        """,
        parameters=(
            str(uuid.uuid4()),
            table_id,
            row["catalog_name"],
            row["schema_name"],
            row["table_name"],
            row["snapshot_id"],
            row["parent_snapshot_id"],
            row["operation"],
            row["last_updated_time"],
            row["batch_added_rows"],
            row["batch_added_files"],
            row["deleted_rows"],
            row["deleted_files"],
            row["table_total_rows"],
            row["table_total_files"],
            row["table_total_size_bytes"],
            row["changed_partition_count"],
            row["schema_id"],
            row["latest_sequence_number"],
            row["metadata_recorded_at"],
            row["collected_at"],
        ),
    )


def collect_table_metadata(
    trino_hook: TrinoHook,
    pg_hook: PostgresHook,
    full_table_name: str,
    date_hour: str,
) -> None:
    schema_name, table_name = split_table_name(full_table_name)
    table_id = get_table_id(
        pg_hook=pg_hook,
        catalog_name=ICEBERG_CATALOG,
        schema_name=schema_name,
        table_name=table_name,
    )

    if table_id is None:
        logger.warning("Skipping unregistered DataGate table: %s.%s.%s", ICEBERG_CATALOG, schema_name, table_name)
        return

    table_rows = fetch_all_as_dicts(
        trino_hook,
        build_table_metadata_sql(
            full_table_name=full_table_name,
            date_hour=date_hour,
        ),
    )

    if not table_rows:
        logger.warning("No table metadata found for %s", full_table_name)
        return

    table_row = table_rows[0]
    upsert_table_metadata(pg_hook, table_id, table_row)

    logger.info(
        "Collected metadata for %s: snapshot=%s",
        full_table_name,
        table_row["snapshot_id"],
    )


def collect_metadata(
    trino_conn_id: str,
    table_names: Sequence[str],
    date_hour: str,
    datagate_db_conn_id: str = DEFAULT_DATAGATE_DB_CONN_ID,
) -> None:
    if not table_names:
        raise ValueError("table_names must not be empty.")

    trino_hook = TrinoHook(trino_conn_id=trino_conn_id)
    pg_hook = PostgresHook(postgres_conn_id=datagate_db_conn_id)

    for full_table_name in table_names:
        collect_table_metadata(
            trino_hook=trino_hook,
            pg_hook=pg_hook,
            full_table_name=full_table_name,
            date_hour=date_hour,
        )
