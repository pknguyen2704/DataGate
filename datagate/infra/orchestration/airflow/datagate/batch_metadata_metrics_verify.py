import logging
import uuid
from contextlib import suppress
from datetime import datetime

from airflow.providers.postgres.hooks.postgres import PostgresHook
from psycopg2.extras import execute_values


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


METADATA_METRICS = {
    "batch_added_rows",
    "batch_added_files",
    "batch_added_files_size_bytes",
    "table_total_rows",
    "table_total_files",
    "table_total_size_bytes",
}


def validate_name(value, field_name):
    value = str(value or "").strip()
    if not value:
        raise ValueError(f"{field_name} must not be empty.")
    for char in value:
        if not (char.isalnum() or char == "_" or char == " "):
            raise ValueError(f"Invalid {field_name}: {value}.")
    return value


def normalize_processing_date_hour(value):
    value = str(value or "").strip().replace("T", " ")
    if not value:
        raise ValueError("processing_date_hour must not be empty.")
    return datetime.fromisoformat(value).strftime("%Y-%m-%d %H:%M:%S")


def evaluate_status(value, min_threshold, max_threshold):
    if value is None:
        return "fail"
    if min_threshold is not None and value < min_threshold:
        return "fail"
    if max_threshold is not None and value > max_threshold:
        return "fail"
    return "pass"


def get_connection_config(pg_hook, connection_name):
    row = pg_hook.get_first(
        """
        SELECT iceberg_catalog_name
        FROM connections
        WHERE connection_name = %s
          AND is_active = TRUE
        LIMIT 1
        """,
        parameters=(validate_name(connection_name, "connection_name"),),
    )
    if row is None:
        raise ValueError(f"No active connection found: {connection_name}")
    return {"catalog_name": validate_name(row[0], "iceberg_catalog_name")}


def get_active_table_ids(pg_hook, catalog_name, schema_name):
    rows = pg_hook.get_records(
        """
        SELECT id
        FROM tables
        WHERE catalog_name = %s
          AND schema_name = %s
        """,
        parameters=(catalog_name, validate_name(schema_name, "schema_name")),
    )
    return [str(row[0]) for row in rows]


def get_metadata_rows(pg_hook, table_ids, processing_date_hour):
    return pg_hook.get_records(
        """
        SELECT
            m.id,
            m.table_id,
            m.metric_name,
            m.min_threshold,
            m.max_threshold,
            m.severity_level,
            b.metric_value
        FROM quality_thresholds m
        JOIN quality_metric_observations b
          ON b.table_id = m.table_id
         AND b.processing_date_hour = %s
         AND b.metric_scope = 'metadata'
         AND b.metric_name = m.metric_name
        WHERE m.table_id = ANY(%s::uuid[])
          AND m.metric_scope = 'metadata'
          AND m.is_active = TRUE
        """,
        parameters=(processing_date_hour, table_ids),
    )


def build_metadata_results(rows, processing_date_hour):
    results = []
    for row in rows:
        (
            threshold_id,
            table_id,
            metric_name,
            min_th,
            max_th,
            severity,
            actual_value,
        ) = row
        if metric_name not in METADATA_METRICS:
            continue
        results.append(
            (
                str(uuid.uuid4()),
                table_id,
                "metadata_threshold",
                threshold_id,
                metric_name,
                actual_value,
                evaluate_status(actual_value, min_th, max_th),
                min_th,
                max_th,
                severity,
                processing_date_hour,
            )
        )
    return results


def save_metadata_results(pg_hook, rows):
    if not rows:
        return

    sql = """
        DELETE FROM quality_check_results
        WHERE check_type = 'metadata_threshold'
          AND processing_date_hour = %s
          AND table_id = ANY(%s::uuid[])
    """
    pg_hook.run(sql, parameters=(rows[0][-1], list({row[1] for row in rows})))

    sql = """
        INSERT INTO quality_check_results (
            id, table_id, check_type, threshold_id, metric_name, actual_value,
            status, min_threshold, max_threshold, severity_level, is_resolved,
            processing_date_hour, created_at, updated_at
        )
        VALUES %s
    """

    conn = pg_hook.get_conn()
    with conn.cursor() as cursor:
        execute_values(
            cursor,
            sql,
            rows,
            template="(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, FALSE, %s, NOW(), NOW())",
        )
    conn.commit()


def close_pg_hook(pg_hook):
    if pg_hook is None:
        return

    with suppress(Exception):
        conn = getattr(pg_hook, "conn", None)
        if conn is not None and not conn.closed:
            conn.close()


def evaluate_metadata_metrics(
    datagate_db_conn_id, connection_name, schema_name, processing_date_hour
):
    processing_date_hour = normalize_processing_date_hour(processing_date_hour)
    pg_hook = PostgresHook(postgres_conn_id=datagate_db_conn_id)

    try:
        config = get_connection_config(pg_hook, connection_name)
        table_ids = get_active_table_ids(pg_hook, config["catalog_name"], schema_name)

        if not table_ids:
            logger.info(
                "No active tables found | connection=%s | schema=%s",
                connection_name,
                schema_name,
            )
            return True

        rows = get_metadata_rows(pg_hook, table_ids, processing_date_hour)
        results = build_metadata_results(rows, processing_date_hour)
        save_metadata_results(pg_hook, results)

        passed = sum(row[4] == "pass" for row in results)
        failed = sum(row[4] == "fail" for row in results)

        logger.info(
            "Metadata metrics evaluated | connection=%s | schema=%s | hour=%s | total=%s | pass=%s | fail=%s",
            connection_name,
            schema_name,
            processing_date_hour,
            len(results),
            passed,
            failed,
        )

        return True

    finally:
        close_pg_hook(pg_hook)
