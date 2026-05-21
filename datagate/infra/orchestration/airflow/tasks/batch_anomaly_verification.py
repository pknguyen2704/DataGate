import logging
import uuid
from contextlib import suppress
from datetime import datetime

from airflow.providers.postgres.hooks.postgres import PostgresHook
from psycopg2.extras import execute_values


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

def evaluate_auc_status(auc_score, max_threshold):
    if auc_score is None:
        return "fail"
    if max_threshold is None:
        return "fail"
    if auc_score > max_threshold:
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
        parameters=(connection_name,),
    )

    if row is None:
        raise ValueError(f"No active connection found with connection_name={connection_name}")

    return {
        "connection_id": str(row[0]),
        "catalog_name": validate_name(row[1], "catalog_name"),
    }

# Get active table ids from Datagate database
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
        parameters=(connection_id, catalog_name, schema_name),
    )

    return [str(row[0]) for row in rows]

def get_auc_rows(pg_hook, table_ids, processing_date_hour):
    if not table_ids:
        return []

    return pg_hook.get_records(
        """
        WITH latest_auc_thresholds AS (
            SELECT DISTINCT ON (table_id)
                id,
                table_id,
                max_threshold,
                severity_level
            FROM quality_thresholds
            WHERE table_id = ANY(%s::uuid[])
              AND check_type = 'anomaly'
              AND metric_name = 'auc_score'
              AND is_active = TRUE
              AND max_threshold IS NOT NULL
            ORDER BY
                table_id,
                updated_at DESC NULLS LAST,
                created_at DESC NULLS LAST
        )
        SELECT
            t.id AS threshold_id,
            t.table_id,
            t.max_threshold,
            t.severity_level,
            a.id AS anomaly_result_id,
            a.auc_score
        FROM latest_auc_thresholds t
        JOIN anomaly_results a
          ON a.table_id = t.table_id
         AND a.processing_date_hour = %s::timestamp
        """,
        parameters=(table_ids, processing_date_hour),
    )


def build_auc_results(rows, processing_date_hour):
    if not rows:
        return []
    results = []
    for row in rows:
        (
            threshold_id,
            table_id,
            max_threshold,
            severity_level,
            anomaly_result_id,
            auc_score,
        ) = row

        actual_value = float(auc_score) if auc_score is not None else None
        max_threshold_value = float(max_threshold) if max_threshold is not None else None
        status = evaluate_auc_status(actual_value,max_threshold_value)

        results.append(
            (
                str(uuid.uuid4()),
                table_id,
                "anomaly",
                threshold_id,
                anomaly_result_id,
                "auc_score",
                actual_value,
                max_threshold_value,
                status,
                severity_level or "warning",
                processing_date_hour,
            )
        )

    return results

def save_auc_results(pg_hook, rows):
    if not rows:
        return

    sql = """
        INSERT INTO quality_check_results (
            id,
            table_id,
            check_type,
            threshold_id,
            anomaly_result_id,
            metric_name,
            actual_value,
            max_threshold,
            status,
            severity_level,
            is_resolved,
            processing_date_hour,
            created_at,
            updated_at
        )
        VALUES %s
        ON CONFLICT (table_id, check_type, threshold_id, processing_date_hour) WHERE threshold_id IS NOT NULL
        DO UPDATE SET
            anomaly_result_id = EXCLUDED.anomaly_result_id,
            metric_name = EXCLUDED.metric_name,
            actual_value = EXCLUDED.actual_value,
            max_threshold = EXCLUDED.max_threshold,
            status = EXCLUDED.status,
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
            template="(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, FALSE, %s, NOW(), NOW())",
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

# PythonOperator entrypoint
def batch_anomaly_verification(
    datagate_db_conn_id,
    connection_name,
    schema_name,
    processing_date_hour,
):
    connection_name = validate_name(connection_name, "connection_name")
    schema_name = validate_name(schema_name, "schema_name")
    processing_date_hour = normalize_processing_date_hour(processing_date_hour)
    pg_hook = PostgresHook(postgres_conn_id=datagate_db_conn_id)

    try:
        config = get_connection_config(pg_hook, connection_name)
        table_ids = get_active_table_ids(pg_hook,config["connection_id"],config["catalog_name"],schema_name)

        if not table_ids:
            logger.info(
                "No active tables found | connection=%s | schema=%s",
                connection_name,
                schema_name,
            )
            return True

        rows = get_auc_rows(pg_hook,table_ids,processing_date_hour)

        results = build_auc_results(rows,processing_date_hour,)

        save_auc_results(
            pg_hook=pg_hook,
            rows=results,
        )

        passed = sum(row[8] == "pass" for row in results)
        failed = sum(row[8] == "fail" for row in results)

        logger.info(
            "Anomaly metrics evaluated | connection=%s | schema=%s | hour=%s | total=%s | pass=%s | fail=%s",
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