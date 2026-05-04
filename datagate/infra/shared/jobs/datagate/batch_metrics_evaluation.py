import argparse
import logging
import uuid
from datetime import datetime

from airflow.providers.postgres.hooks.postgres import PostgresHook
from psycopg2.extras import execute_values


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

JOB_NAME = "batch_metric_evaluation"


METADATA_METRIC_COLUMNS = {
    "batch_added_rows": "batch_added_rows",
    "batch_added_files": "batch_added_files",
    "deleted_rows": "deleted_rows",
    "deleted_files": "deleted_files",
    "table_total_rows": "table_total_rows",
    "table_total_files": "table_total_files",
    "table_total_size_bytes": "table_total_size_bytes",
}

PROFILING_METRIC_COLUMNS = {
    "completeness": "completeness",
    "mean": "mean",
    "standard_deviation": "standard_deviation",
    "minimum": "minimum",
    "maximum": "maximum",
    "min_length": "min_length",
    "max_length": "max_length",
    "distinctness": "distinctness",
    "approx_count_distinct": "approx_count_distinct",
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Evaluate metadata/profiling metrics against manual thresholds"
    )

    parser.add_argument(
        "--datagate_db_conn_id",
        default="datagate_db_default",
    )

    parser.add_argument("--connection_name", required=True)

    parser.add_argument(
        "--schema_name",
        required=False,
        default=None,
        help="Optional. If provided, only evaluate tables in this schema.",
    )

    parser.add_argument(
        "--processing_date_hour",
        required=True,
        help="Processing batch hour, format: yyyy-MM-dd HH:mm:ss",
    )

    return parser.parse_args()


def normalize_processing_date_hour(value):
    if value is None:
        raise ValueError("processing_date_hour must not be None.")

    value = str(value).strip().replace("T", " ")

    if value == "":
        raise ValueError("processing_date_hour must not be empty.")

    dt = datetime.fromisoformat(value)

    return dt.strftime("%Y-%m-%d %H:%M:%S")


def get_active_thresholds(pg_hook, connection_name, schema_name=None):
    filters = [
        "c.name = %s",
        "c.is_active = TRUE",
        "t.is_active = TRUE",
        "m.is_active = TRUE",
    ]

    params = [connection_name]

    if schema_name:
        filters.append("t.schema_name = %s")
        params.append(schema_name)

    where_clause = " AND ".join(filters)

    sql = f"""
        SELECT
            m.id,
            m.table_id,
            m.metric_group,
            m.column_name,
            m.metric_name,
            m.min_threshold,
            m.max_threshold,
            m.severity_level,
            t.catalog_name,
            t.schema_name,
            t.table_name
        FROM metric_manual_thresholds m
        JOIN tables t
          ON t.id = m.table_id
        JOIN connections c
          ON c.id = t.connection_id
        WHERE {where_clause}
        ORDER BY
            t.schema_name,
            t.table_name,
            m.metric_group,
            m.column_name,
            m.metric_name
    """

    rows = pg_hook.get_records(sql, parameters=tuple(params))

    thresholds = []

    for row in rows:
        thresholds.append(
            {
                "metric_manual_threshold_id": str(row[0]),
                "table_id": str(row[1]),
                "metric_group": row[2],
                "column_name": row[3],
                "metric_name": row[4],
                "min_threshold": row[5],
                "max_threshold": row[6],
                "severity_level": row[7],
                "catalog_name": row[8],
                "schema_name": row[9],
                "table_name": row[10],
            }
        )

    return thresholds


def get_metadata_actual_value(pg_hook, table_id, metric_name, processing_date_hour):
    metric_column = METADATA_METRIC_COLUMNS.get(metric_name)

    if metric_column is None:
        return None, f"Unsupported metadata metric_name: {metric_name}"

    sql = f"""
        SELECT {metric_column}::double precision AS actual_value
        FROM table_batch_metadata
        WHERE table_id = %s
          AND processing_date_hour = %s
        ORDER BY created_at DESC
        LIMIT 1
    """

    row = pg_hook.get_first(
        sql,
        parameters=(table_id, processing_date_hour),
    )

    if row is None:
        return None, "No metadata result found for this batch."

    return row[0], None


def get_profiling_actual_value(
    pg_hook,
    table_id,
    column_name,
    metric_name,
    processing_date_hour,
):
    metric_column = PROFILING_METRIC_COLUMNS.get(metric_name)

    if metric_column is None:
        return None, f"Unsupported profiling metric_name: {metric_name}"

    sql = f"""
        SELECT {metric_column}::double precision AS actual_value
        FROM batch_table_profiling
        WHERE table_id = %s
          AND column_name = %s
          AND processing_date_hour = %s
        ORDER BY created_at DESC
        LIMIT 1
    """

    row = pg_hook.get_first(
        sql,
        parameters=(table_id, column_name, processing_date_hour),
    )

    if row is None:
        return None, "No profiling result found for this batch."

    return row[0], None


def get_actual_value(pg_hook, threshold, processing_date_hour):
    metric_group = threshold["metric_group"]

    if metric_group == "metadata":
        return get_metadata_actual_value(
            pg_hook=pg_hook,
            table_id=threshold["table_id"],
            metric_name=threshold["metric_name"],
            processing_date_hour=processing_date_hour,
        )

    if metric_group == "profiling":
        return get_profiling_actual_value(
            pg_hook=pg_hook,
            table_id=threshold["table_id"],
            column_name=threshold["column_name"],
            metric_name=threshold["metric_name"],
            processing_date_hour=processing_date_hour,
        )

    return None, f"Unsupported metric_group: {metric_group}"


def evaluate_threshold(threshold, actual_value, error_message=None):
    min_threshold = threshold["min_threshold"]
    max_threshold = threshold["max_threshold"]

    if error_message:
        return "fail", error_message

    if min_threshold is None and max_threshold is None:
        return "pass", "No min/max threshold configured. Treated as pass."

    if actual_value is None:
        return "fail", "Actual value is null."

    if min_threshold is not None and actual_value < min_threshold:
        return (
            "fail",
            f"Actual value {actual_value} is lower than min_threshold {min_threshold}.",
        )

    if max_threshold is not None and actual_value > max_threshold:
        return (
            "fail",
            f"Actual value {actual_value} is higher than max_threshold {max_threshold}.",
        )

    return (
        "pass",
        f"Actual value {actual_value} is within configured threshold.",
    )


def build_result_row(threshold, actual_value, status, message, processing_date_hour):
    return {
        "metric_manual_threshold_id": threshold["metric_manual_threshold_id"],
        "actual_value": actual_value,
        "status": status,
        "min_threshold": threshold["min_threshold"],
        "max_threshold": threshold["max_threshold"],
        "severity_level": threshold["severity_level"],
        "message": message,
        "processing_date_hour": processing_date_hour,
    }


def save_metric_results(pg_hook, rows):
    if not rows:
        return

    sql = """
        INSERT INTO metric_results (
            id,
            metric_manual_threshold_id,
            actual_value,
            status,
            min_threshold,
            max_threshold,
            severity_level,
            message,
            processing_date_hour,
            created_at
        )
        VALUES %s
        ON CONFLICT (
            metric_manual_threshold_id,
            processing_date_hour
        )
        DO UPDATE SET
            actual_value = EXCLUDED.actual_value,
            status = EXCLUDED.status,
            min_threshold = EXCLUDED.min_threshold,
            max_threshold = EXCLUDED.max_threshold,
            severity_level = EXCLUDED.severity_level,
            message = EXCLUDED.message,
            created_at = EXCLUDED.created_at
    """

    now = datetime.utcnow()

    values = []

    for row in rows:
        values.append(
            (
                str(uuid.uuid4()),
                row["metric_manual_threshold_id"],
                row["actual_value"],
                row["status"],
                row["min_threshold"],
                row["max_threshold"],
                row["severity_level"],
                row["message"],
                row["processing_date_hour"],
                now,
            )
        )

    conn = pg_hook.get_conn()

    with conn.cursor() as cursor:
        execute_values(cursor, sql, values)

    conn.commit()


def main():
    args = parse_args()

    processing_date_hour = normalize_processing_date_hour(
        args.processing_date_hour
    )

    pg_hook = PostgresHook(
        postgres_conn_id=args.datagate_db_conn_id
    )

    thresholds = get_active_thresholds(
        pg_hook=pg_hook,
        connection_name=args.connection_name,
        schema_name=args.schema_name,
    )

    if not thresholds:
        logger.info(
            "No active metric thresholds found | connection=%s | schema=%s",
            args.connection_name,
            args.schema_name,
        )
        return

    result_rows = []

    for threshold in thresholds:
        actual_value, error_message = get_actual_value(
            pg_hook=pg_hook,
            threshold=threshold,
            processing_date_hour=processing_date_hour,
        )

        status, message = evaluate_threshold(
            threshold=threshold,
            actual_value=actual_value,
            error_message=error_message,
        )

        result_rows.append(
            build_result_row(
                threshold=threshold,
                actual_value=actual_value,
                status=status,
                message=message,
                processing_date_hour=processing_date_hour,
            )
        )

        logger.info(
            "Metric evaluated | table=%s.%s | column=%s | metric=%s | value=%s | status=%s",
            threshold["schema_name"],
            threshold["table_name"],
            threshold["column_name"],
            threshold["metric_name"],
            actual_value,
            status,
        )

    save_metric_results(
        pg_hook=pg_hook,
        rows=result_rows,
    )

    pass_count = sum(1 for row in result_rows if row["status"] == "pass")
    fail_count = sum(1 for row in result_rows if row["status"] == "fail")

    logger.info(
        "Metric evaluation completed | total=%s | pass=%s | fail=%s | processing_date_hour=%s",
        len(result_rows),
        pass_count,
        fail_count,
        processing_date_hour,
    )


if __name__ == "__main__":
    main()