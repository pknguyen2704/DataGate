from __future__ import annotations

from pprint import pprint
from typing import Sequence

from airflow.providers.trino.hooks.trino import TrinoHook


ICEBERG_CATALOG = "iceberg"


def split_table_name(full_table_name: str) -> tuple[str, str]:
    """
    Example:
        bronze.yellow_tripdata
        -> ("bronze", "yellow_tripdata")
    """
    parts = full_table_name.split(".", 1)

    if len(parts) != 2:
        raise ValueError(
            f"Invalid table name: {full_table_name}. "
            "Expected format: <schema_name>.<table_name>"
        )

    schema_name, table_name = parts
    return schema_name, table_name


def infer_layer(schema_name: str) -> str:
    schema_name = schema_name.lower()

    if schema_name in {"bronze", "silver", "gold"}:
        return schema_name

    return "unknown"


def fetch_all_as_dicts(hook: TrinoHook, sql: str) -> list[dict]:
    """
    Execute SQL and return rows as list[dict].
    """
    records = hook.get_records(sql)

    if not records:
        return []

    cursor = hook.get_cursor()
    cursor.execute(sql)

    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()

    return [dict(zip(columns, row)) for row in rows]


def build_table_metadata_sql(full_table_name: str, date_hour: str) -> str:
    schema_name, table_name = split_table_name(full_table_name)
    layer = infer_layer(schema_name)

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
        '{layer}' AS layer,

        '{ICEBERG_CATALOG}' AS catalog_name,
        '{schema_name}' AS schema_name,
        '{table_name}' AS table_name,

        s.snapshot_id,
        s.parent_id AS parent_snapshot_id,
        s.operation,
        s.committed_at AS last_updated_time,

        COALESCE(
            TRY_CAST(element_at(s.summary, 'added-records') AS BIGINT),
            0
        ) AS batch_added_rows,

        COALESCE(
            TRY_CAST(element_at(s.summary, 'added-data-files') AS BIGINT),
            TRY_CAST(element_at(s.summary, 'added-files') AS BIGINT),
            0
        ) AS batch_added_files,

        COALESCE(
            TRY_CAST(element_at(s.summary, 'deleted-records') AS BIGINT),
            0
        ) AS deleted_rows,

        COALESCE(
            TRY_CAST(element_at(s.summary, 'deleted-data-files') AS BIGINT),
            TRY_CAST(element_at(s.summary, 'deleted-files') AS BIGINT),
            0
        ) AS deleted_files,

        TRY_CAST(element_at(s.summary, 'total-records') AS BIGINT)
            AS table_total_rows,

        TRY_CAST(element_at(s.summary, 'total-data-files') AS BIGINT)
            AS table_total_files,

        TRY_CAST(element_at(s.summary, 'total-files-size') AS BIGINT)
            AS table_total_size_bytes,

        COALESCE(
            TRY_CAST(element_at(s.summary, 'changed-partition-count') AS BIGINT),
            0
        ) AS changed_partition_count,

        m.latest_schema_id AS schema_id,
        m.latest_sequence_number,
        m.metadata_recorded_at,

        date_diff('minute', s.committed_at, current_timestamp)
            AS freshness_lag_minutes,

        current_timestamp AS collected_at

    FROM latest_snapshot s
    LEFT JOIN latest_metadata m
        ON m.latest_snapshot_id = s.snapshot_id
    """


def build_column_metadata_sql(full_table_name: str, date_hour: str) -> str:
    schema_name, table_name = split_table_name(full_table_name)
    layer = infer_layer(schema_name)

    return f"""
    WITH latest_snapshot AS (
        SELECT
            snapshot_id
        FROM {ICEBERG_CATALOG}.{schema_name}."{table_name}$snapshots"
        ORDER BY committed_at DESC
        LIMIT 1
    ),

    latest_metadata AS (
        SELECT
            latest_snapshot_id,
            latest_schema_id
        FROM {ICEBERG_CATALOG}.{schema_name}."{table_name}$metadata_log_entries"
        ORDER BY timestamp DESC
        LIMIT 1
    )

    SELECT
        TIMESTAMP '{date_hour}' AS date_hour,
        '{layer}' AS layer,

        '{ICEBERG_CATALOG}' AS catalog_name,
        c.table_schema AS schema_name,
        c.table_name,

        s.snapshot_id,
        m.latest_schema_id AS schema_id,

        c.column_name,
        c.data_type AS column_type,
        c.ordinal_position,
        c.is_nullable,

        current_timestamp AS collected_at

    FROM {ICEBERG_CATALOG}.information_schema.columns c
    CROSS JOIN latest_snapshot s
    LEFT JOIN latest_metadata m
        ON m.latest_snapshot_id = s.snapshot_id
    WHERE c.table_schema = '{schema_name}'
      AND c.table_name = '{table_name}'
    ORDER BY c.ordinal_position
    """


def print_table_metadata(
    hook: TrinoHook,
    full_table_name: str,
    date_hour: str,
) -> None:
    print("=" * 100)
    print(f"[METADATA COLLECTION] Table: {full_table_name}")
    print("=" * 100)

    table_metadata_sql = build_table_metadata_sql(
        full_table_name=full_table_name,
        date_hour=date_hour,
    )

    column_metadata_sql = build_column_metadata_sql(
        full_table_name=full_table_name,
        date_hour=date_hour,
    )

    print("\n[TABLE-LEVEL METADATA]")
    table_rows = fetch_all_as_dicts(hook, table_metadata_sql)

    if not table_rows:
        print(f"No table-level metadata found for {full_table_name}")
    else:
        for row in table_rows:
            pprint(row, sort_dicts=False)

    print("\n[COLUMN-LEVEL METADATA]")
    column_rows = fetch_all_as_dicts(hook, column_metadata_sql)

    if not column_rows:
        print(f"No column-level metadata found for {full_table_name}")
    else:
        for row in column_rows:
            pprint(row, sort_dicts=False)

    print("\n")


def collect_metadata(
    trino_conn_id: str,
    table_names: Sequence[str],
    date_hour: str,
) -> None:
    if not table_names:
        raise ValueError("table_names must not be empty.")

    print("=" * 100)
    print("[METADATA COLLECTION STARTED]")
    print(f"trino_conn_id: {trino_conn_id}")
    print(f"date_hour: {date_hour}")
    print(f"table_count: {len(table_names)}")
    print("=" * 100)

    hook = TrinoHook(trino_conn_id=trino_conn_id)

    for full_table_name in table_names:
        print_table_metadata(
            hook=hook,
            full_table_name=full_table_name,
            date_hour=date_hour,
        )

    print("=" * 100)
    print("[METADATA COLLECTION FINISHED]")
    print("=" * 100)