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

# Evaluate check status with thresholds
def evaluate_status(value, min_threshold, max_threshold):
    if value is None:
        return "fail"
    if min_threshold is not None and value < min_threshold:
        return "fail"
    if max_threshold is not None and value > max_threshold:
        return "fail"
    return "pass"

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


def get_active_table_ids(pg_hook, connection_id, catalog_name, schema_name):
    rows = pg_hook.get_records(
        """
        SELECT id
        FROM tables
        WHERE connection_id = %s
          AND catalog_name = %s
          AND schema_name = %s
          AND is_active = TRUE
        """,
        parameters=(connection_id, catalog_name, schema_name)
    )
    return [str(row[0]) for row in rows]


def get_profiling_rows(pg_hook, table_ids, processing_date_hour):
    return pg_hook.get_records(
        """
        SELECT
            m.id,
            m.table_id,
            m.column_name,
            m.metric_name,
            m.min_threshold,
            m.max_threshold,
            m.severity_level,
            CASE m.metric_name
                WHEN 'completeness' THEN p.completeness
                WHEN 'mean' THEN p.mean
                WHEN 'standard_deviation' THEN p.standard_deviation
                WHEN 'minimum' THEN p.minimum
                WHEN 'maximum' THEN p.maximum
                WHEN 'min_length' THEN p.min_length::float
                WHEN 'max_length' THEN p.max_length::float
                WHEN 'distinctness' THEN p.distinctness
                WHEN 'approx_count_distinct' THEN p.approx_count_distinct::float
            END AS actual_value
        FROM quality_thresholds m
        JOIN batch_table_profiling p
          ON p.table_id = m.table_id
         AND p.column_name = m.column_name
         AND p.processing_date_hour = %s
        WHERE m.table_id = ANY(%s::uuid[])
          AND m.check_type = 'profiling'
          AND m.is_active = TRUE
        """,
        parameters=(processing_date_hour, table_ids)
    )


def build_profiling_results(rows, processing_date_hour):
    results = []
    for row in rows:
        (
            threshold_id,
            table_id,
            column_name,
            metric_name,
            min_th,
            max_th,
            severity,
            actual_value,
        ) = row
        if metric_name not in PROFILING_METRICS:
            continue
        results.append(
            (
                str(uuid.uuid4()),
                table_id,
                "profiling",
                threshold_id,
                column_name,
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

def save_profiling_results(pg_hook, rows):
    if not rows:
        return

    sql = """
        INSERT INTO quality_check_results (
            id, table_id, check_type, threshold_id, column_name, metric_name,
            actual_value, status, min_threshold, max_threshold, severity_level,
            is_resolved, processing_date_hour, created_at, updated_at
        )
        VALUES %s
        ON CONFLICT (table_id, check_type, threshold_id, processing_date_hour) WHERE threshold_id IS NOT NULL
        DO UPDATE SET
            column_name = EXCLUDED.column_name,
            metric_name = EXCLUDED.metric_name,
            actual_value = EXCLUDED.actual_value,
            status = EXCLUDED.status,
            min_threshold = EXCLUDED.min_threshold,
            max_threshold = EXCLUDED.max_threshold,
            severity_level = EXCLUDED.severity_level,
            is_resolved = FALSE,
            updated_at = NOW()
    """

    conn = pg_hook.get_conn()

    with conn.cursor() as cursor:
        execute_values(
            cursor,
            sql,
            rows,
            template="(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, FALSE, %s, NOW(), NOW())",
        )

    conn.commit()


# Close hook connection
def close_hook_connection(hook):
    if hook is None:
        return
    for attr_name in ("conn", "_conn"):
        with suppress(Exception):
            conn = getattr(hook, attr_name, None)
            if conn is not None:
                conn.close()

def batch_profiling_metric_verification(
    datagate_db_conn_id, connection_name, schema_name, processing_date_hour
):
    connection_name = validate_name(connection_name, "connection_name")
    schema_name = validate_name(schema_name, "schema_name")
    processing_date_hour = normalize_processing_date_hour(processing_date_hour)
    pg_hook = PostgresHook(postgres_conn_id=datagate_db_conn_id)

    try:
        config = get_connection_config(pg_hook, connection_name)
        table_ids = get_active_table_ids(pg_hook, config["connection_id"], config["catalog_name"], schema_name)

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

        passed = sum(row[7] == "pass" for row in results)
        failed = sum(row[7] == "fail" for row in results)

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
        close_hook_connection(pg_hook)
