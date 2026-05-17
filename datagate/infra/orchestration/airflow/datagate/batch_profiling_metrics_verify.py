import logging
import uuid
from contextlib import suppress
from datetime import datetime

from airflow.providers.postgres.hooks.postgres import PostgresHook
from psycopg2.extras import execute_values


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


PROFILING_METRICS = {
    "completeness",
    "mean",
    "standard_deviation",
    "minimum",
    "maximum",
    "min_length",
    "max_length",
    "distinctness",
    "approx_count_distinct",
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
          AND is_active = TRUE
        """,
        parameters=(catalog_name, validate_name(schema_name, "schema_name")),
    )
    return [str(row[0]) for row in rows]


def get_profiling_rows(pg_hook, table_ids, processing_date_hour):
    return pg_hook.get_records(
        """
        SELECT
            m.id,
            p.id,
            m.metric_name,
            m.min_threshold,
            m.max_threshold,
            m.severity_level,
            p.completeness,
            p.mean,
            p.standard_deviation,
            p.minimum,
            p.maximum,
            p.min_length,
            p.max_length,
            p.distinctness,
            p.approx_count_distinct
        FROM batch_table_profiling_manual_thresholds m
        JOIN batch_table_profiling p
          ON p.table_id = m.table_id
         AND p.column_name = m.column_name
         AND p.processing_date_hour = %s
        WHERE m.table_id = ANY(%s::uuid[])
          AND m.is_active = TRUE
        """,
        parameters=(processing_date_hour, table_ids),
    )


def build_profiling_results(rows, processing_date_hour):
    results = []
    for row in rows:
        (
            threshold_id,
            batch_id,
            metric_name,
            min_th,
            max_th,
            severity,
            completeness,
            mean,
            std,
            min_v,
            max_v,
            min_len,
            max_len,
            distinctness,
            approx_distinct,
        ) = row
        values = {
            "completeness": completeness,
            "mean": mean,
            "standard_deviation": std,
            "minimum": min_v,
            "maximum": max_v,
            "min_length": min_len,
            "max_length": max_len,
            "distinctness": distinctness,
            "approx_count_distinct": approx_distinct,
        }
        if metric_name not in PROFILING_METRICS:
            continue
        actual_value = values.get(metric_name)
        results.append(
            (
                str(uuid.uuid4()),
                threshold_id,
                batch_id,
                actual_value,
                evaluate_status(actual_value, min_th, max_th),
                min_th,
                max_th,
                severity,
                processing_date_hour,
            )
        )
    return results


def save_profiling_results(pg_hook, rows):
    if not rows:
        return

    sql = """
        INSERT INTO batch_table_profiling_metrics_verify (
            id,
            profiling_manual_threshold_id,
            batch_table_profiling_id,
            actual_value,
            status,
            min_threshold,
            max_threshold,
            severity_level,
            is_resolved,
            processing_date_hour,
            created_at,
            updated_at
        )
        VALUES %s
        ON CONFLICT (profiling_manual_threshold_id, batch_table_profiling_id)
        DO UPDATE SET
            actual_value = EXCLUDED.actual_value,
            status = EXCLUDED.status,
            min_threshold = EXCLUDED.min_threshold,
            max_threshold = EXCLUDED.max_threshold,
            severity_level = EXCLUDED.severity_level,
            is_resolved = FALSE,
            resolved_by = NULL,
            processing_date_hour = EXCLUDED.processing_date_hour,
            updated_at = NOW()
    """

    conn = pg_hook.get_conn()
    with conn.cursor() as cursor:
        execute_values(
            cursor,
            sql,
            rows,
            template="(%s, %s, %s, %s, %s, %s, %s, %s, FALSE, %s, NOW(), NOW())",
        )
    conn.commit()


def close_pg_hook(pg_hook):
    if pg_hook is None:
        return

    with suppress(Exception):
        conn = getattr(pg_hook, "conn", None)
        if conn is not None and not conn.closed:
            conn.close()


def evaluate_profiling_metrics(
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

        rows = get_profiling_rows(pg_hook, table_ids, processing_date_hour)
        results = build_profiling_results(rows, processing_date_hour)
        save_profiling_results(pg_hook, results)

        passed = sum(row[4] == "pass" for row in results)
        failed = sum(row[4] == "fail" for row in results)

        logger.info(
            "Profiling metrics evaluated | connection=%s | schema=%s | hour=%s | total=%s | pass=%s | fail=%s",
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
