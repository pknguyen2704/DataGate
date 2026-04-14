from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.trino.hooks.trino import TrinoHook
from airflow.providers.postgres.hooks.postgres import PostgresHook
import logging
from datetime import datetime, timedelta, timezone
import requests
import json

default_args = {
    'owner': 'datagate',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'dq_metadata_collector',
    default_args=default_args,
    description='Collects metadata from Iceberg via Trino and stores in Postgres (Pillar 1)',
    schedule=None,
    catchup=False
)

def collect_metadata(**kwargs):
    conf = kwargs.get('dag_run').conf or {}
    catalog = conf.get('catalog', 'iceberg')
    schema = conf.get('schema', 'public')
    table_input = conf.get('table')
    
    if not table_input:
        raise ValueError("table must be provided in conf")
        
    # Smart parsing for table_path
    parts = table_input.split(".")
    if len(parts) == 3: # catalog.schema.table
        catalog, schema, table = parts[0], parts[1], parts[2]
    elif len(parts) == 2: # schema.table
        schema, table = parts[0], parts[1]
    else:
        table = table_input

    full_table_name = f"{catalog}.{schema}.{table}"
    logging.info(f"🚀 Starting metadata collection for {full_table_name}")
    
    # 🕵️ Queries
    queries = {
        "existence": f"SELECT COUNT(*) > 0 FROM {catalog}.information_schema.tables WHERE table_schema = '{schema}' AND table_name = '{table}'",
        "freshness": f'SELECT MAX(committed_at) FROM {catalog}.{schema}."{table}$snapshots"',
        "volume": f'SELECT SUM(record_count), SUM(file_size_in_bytes) FROM {catalog}.{schema}."{table}$files"',
        "volume_ts": f"""
            SELECT date_trunc('hour', committed_at) AS dt, SUM(CAST(element_at(summary, 'added-records') AS BIGINT)) 
            FROM {catalog}.{schema}."{table}$snapshots" 
            GROUP BY 1
        """,
        "schema": f"SELECT column_name, data_type FROM {catalog}.information_schema.columns WHERE table_schema = '{schema}' AND table_name = '{table}'",
        "column_stats": f"""
            SELECT column_name, SUM(null_value_count) AS nulls, SUM(value_count) AS total
            FROM {catalog}.{schema}."{table}$files"
            CROSS JOIN UNNEST(map_keys(null_value_counts), map_values(null_value_counts), map_values(value_counts)) AS t(column_name, null_value_count, value_count)
            GROUP BY column_name
        """
    }

    try:
        # 🟢 Trino Hook
        trino_hook = TrinoHook(trino_conn_id='trino_default')
        results = {}
        for key, sql in queries.items():
            try:
                results[key] = trino_hook.get_records(sql)
            except Exception as e:
                logging.warning(f"⚠️ Error running {key} query: {e}")
                results[key] = []

        # 🔵 Postgres Hook
        pg_hook = PostgresHook(postgres_conn_id='datagate_db_default')
        now = datetime.now(timezone.utc)

        # 1. Snapshot
        if results.get("volume") and results["volume"][0][0] is not None:
            last_updated = results["freshness"][0][0] if results.get("freshness") else None
            pg_hook.run(
                "INSERT INTO dq_table_snapshot (table_name, snapshot_time, last_updated_time, total_records, total_size) VALUES (%s, %s, %s, %s, %s)",
                parameters=(full_table_name, now, last_updated, results["volume"][0][0], results["volume"][0][1])
            )

        # 2. Volume TS
        for row in results.get("volume_ts", []):
            if row[0] is not None:
                pg_hook.run(
                    "INSERT INTO dq_table_volume_ts (table_name, dt, records_added) VALUES (%s, %s, %s)",
                    parameters=(full_table_name, row[0], row[1])
                )

        # 3. Schema
        for row in results.get("schema", []):
            pg_hook.run(
                "INSERT INTO dq_table_schema (table_name, column_name, data_type, snapshot_time) VALUES (%s, %s, %s, %s)",
                parameters=(full_table_name, row[0], row[1], now)
            )

        # 4. Column Stats
        for row in results.get("column_stats", []):
            pg_hook.run(
                "INSERT INTO dq_column_stats (table_name, column_name, nulls, total, snapshot_time) VALUES (%s, %s, %s, %s, %s)",
                parameters=(full_table_name, row[0], row[1], row[2], now)
            )

        # 5. Trigger Analysis in Backend
        try:
            from app.core.config import settings
            import requests
            # Inside Docker network, use service name
            backend_url = f"http://datagate_backend:8000/api/v1/observability/analyze?table_name={full_table_name}"
            # For simplicity using basic auth if needed, but endpoint might be internal
            # Here we just try to ping it.
            requests.post(backend_url, timeout=5)
            logging.info(f"⚡️ Triggered backend analysis for {full_table_name}")
        except Exception as e:
            logging.warning(f"⚠️ Could not trigger auto-analysis: {e}")

        logging.info(f"✅ Metadata collection complete for {full_table_name}")

    except Exception as e:
        logging.error(f"❌ Critical failure in metadata collection: {e}")
        raise

run_task = PythonOperator(
    task_id='collect_metadata',
    python_callable=collect_metadata,
    dag=dag,
)
