from datetime import datetime
import logging

from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.trino.hooks.trino import TrinoHook


def log_run_start(pg_hook, job_id, dag_id, dag_run_id, trigger_type, scheduled_for):
    records = pg_hook.get_records(
        """
        INSERT INTO dq_job_run_history (job_id, dag_id, dag_run_id, trigger_type, status, scheduled_for, started_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        parameters=(job_id, dag_id, dag_run_id, trigger_type, "running", scheduled_for, scheduled_for),
    )
    return records[0][0]


def log_run_finish(pg_hook, history_id, status, finished_at, error_message=None):
    pg_hook.run(
        """
        UPDATE dq_job_run_history
        SET status = %s, finished_at = %s, error_message = %s
        WHERE id = %s
        """,
        parameters=(status, finished_at, error_message, history_id),
    )


def upsert_job_last_run(pg_hook, job_id, run_ts):
    pg_hook.run(
        "UPDATE dq_job_config SET last_run_at = %s WHERE id = %s",
        parameters=(run_ts, job_id),
    )


def collect_table_metadata(trino_hook, catalog, schema, table):
    queries = {
        "freshness": f'SELECT MAX(committed_at) FROM {catalog}.{schema}."{table}$snapshots"',
        "volume": f'SELECT SUM(record_count), SUM(file_size_in_bytes) FROM {catalog}.{schema}."{table}$files"',
        "volume_ts": f"""
            SELECT date_trunc('day', committed_at) AS dt,
                   SUM(CAST(element_at(summary, 'added-records') AS BIGINT))
            FROM {catalog}.{schema}."{table}$snapshots"
            GROUP BY 1
        """,
        "schema": f"""
            SELECT column_name, data_type
            FROM {catalog}.information_schema.columns
            WHERE table_schema = '{schema}' AND table_name = '{table}'
            ORDER BY ordinal_position
        """,
        "column_stats": f"""
            SELECT column_name, SUM(null_value_count) AS nulls, SUM(value_count) AS total
            FROM {catalog}.{schema}."{table}$files"
            CROSS JOIN UNNEST(
                map_keys(null_value_counts),
                map_values(null_value_counts),
                map_values(value_counts)
            ) AS t(column_name, null_value_count, value_count)
            GROUP BY column_name
        """,
    }

    results = {}
    for key, sql in queries.items():
        try:
            results[key] = trino_hook.get_records(sql)
        except Exception as exc:
            logging.warning("Query %s failed for %s.%s.%s: %s", key, catalog, schema, table, exc)
            results[key] = []

    return results


def persist_metadata(pg_hook, full_table_name, results, run_ts):
    pg_hook.run("DELETE FROM dq_table_snapshot WHERE table_name = %s AND snapshot_time = %s", parameters=(full_table_name, run_ts))
    pg_hook.run("DELETE FROM dq_table_schema WHERE table_name = %s AND snapshot_time = %s", parameters=(full_table_name, run_ts))
    pg_hook.run("DELETE FROM dq_column_stats WHERE table_name = %s AND snapshot_time = %s", parameters=(full_table_name, run_ts))

    volume_rows = results.get("volume", [])
    freshness_rows = results.get("freshness", [])
    if volume_rows and volume_rows[0][0] is not None:
        pg_hook.run(
            """
            INSERT INTO dq_table_snapshot (table_name, snapshot_time, last_updated_time, total_records, total_size)
            VALUES (%s, %s, %s, %s, %s)
            """,
            parameters=(
                full_table_name,
                run_ts,
                freshness_rows[0][0] if freshness_rows else None,
                volume_rows[0][0],
                volume_rows[0][1],
            ),
        )

    for row in results.get("volume_ts", []):
        if row[0] is None:
            continue
        pg_hook.run("DELETE FROM dq_table_volume_ts WHERE table_name = %s AND dt = %s", parameters=(full_table_name, row[0]))
        pg_hook.run(
            "INSERT INTO dq_table_volume_ts (table_name, dt, records_added) VALUES (%s, %s, %s)",
            parameters=(full_table_name, row[0], row[1]),
        )

    for row in results.get("schema", []):
        pg_hook.run(
            "INSERT INTO dq_table_schema (table_name, column_name, data_type, snapshot_time) VALUES (%s, %s, %s, %s)",
            parameters=(full_table_name, row[0], row[1], run_ts),
        )

    for row in results.get("column_stats", []):
        pg_hook.run(
            "INSERT INTO dq_column_stats (table_name, column_name, nulls, total, snapshot_time) VALUES (%s, %s, %s, %s, %s)",
            parameters=(full_table_name, row[0], row[1], row[2], run_ts),
        )


def execute_metadata_profile_job(job, dag_id, dag_run_id, trigger_type, run_ts):
    pg_hook = PostgresHook(postgres_conn_id="datagate_db_default")
    trino_hook = TrinoHook(trino_conn_id="trino_default")

    job_id = job.get("job_id") or job.get("id")
    catalog = job.get("catalog") or "iceberg"
    schema = job.get("schema_name") or job.get("schema") or "public"
    table_input = job.get("table_name") or job.get("table")

    if not table_input:
        raise ValueError("table_name is required")

    parts = table_input.split(".")
    if len(parts) == 3:
        catalog, schema, table = parts[0], parts[1], parts[2]
    elif len(parts) == 2:
        schema, table = parts[0], parts[1]
    else:
        table = table_input

    full_table_name = f"{catalog}.{schema}.{table}"
    history_id = log_run_start(pg_hook, job_id, dag_id, dag_run_id, trigger_type, run_ts) if job_id else None

    try:
        results = collect_table_metadata(trino_hook, catalog, schema, table)
        persist_metadata(pg_hook, full_table_name, results, run_ts)
        if job_id:
            upsert_job_last_run(pg_hook, job_id, run_ts)
            log_run_finish(pg_hook, history_id, "success", run_ts)
    except Exception as exc:
        if history_id:
            log_run_finish(pg_hook, history_id, "failed", datetime.utcnow(), str(exc))
        raise
