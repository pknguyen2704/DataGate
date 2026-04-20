from datetime import datetime, timedelta
import logging
import os
import sys

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.trino.hooks.trino import TrinoHook

logger = logging.getLogger(__name__)

default_args = {
    "owner": "datagate",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


def ensure_tables(pg_hook: PostgresHook) -> None:
    pg_hook.run(
        """
        CREATE TABLE IF NOT EXISTS table_metrics (
            id BIGSERIAL PRIMARY KEY,
            table_name TEXT NOT NULL,
            layer TEXT NOT NULL,
            ds TIMESTAMP NOT NULL,
            records_added BIGINT,
            bytes_added BIGINT,
            file_count BIGINT,
            delay DOUBLE PRECISION,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (table_name, layer, ds)
        );
        CREATE TABLE IF NOT EXISTS schema_history (
            id BIGSERIAL PRIMARY KEY,
            table_name TEXT NOT NULL,
            column_name TEXT NOT NULL,
            data_type TEXT NOT NULL,
            collected_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        autocommit=True,
    )


def get_target_tables(**kwargs):
    dag_run = kwargs.get("dag_run")
    conf = dag_run.conf if dag_run and dag_run.conf else {}
    tables = conf.get("tables")
    catalog = conf.get("catalog", "iceberg")

    if tables:
        return [
            {
                "catalog": catalog,
                "schema": item["schema"],
                "table": item["table"],
                "layer": item.get("layer", item["schema"]),
            }
            for item in tables
        ]

    pg_hook = PostgresHook(postgres_conn_id="datagate_db_default")
    rows = pg_hook.get_records(
        "SELECT catalog, schema_name, table_name FROM dg_observability_config WHERE is_active = TRUE"
    )
    return [
        {
            "catalog": row[0] or "iceberg",
            "schema": row[1],
            "table": row[2],
            "layer": row[1],
        }
        for row in rows
    ]


def collect_table_metrics(trino_hook: TrinoHook, catalog: str, schema: str, table: str) -> dict:
    joined_query = f"""
        WITH snapshots AS (
            SELECT
                snapshot_id,
                committed_at,
                operation,
                element_at(summary, 'added-records') AS added_records_summary
            FROM {catalog}.{schema}."{table}$snapshots"
        ),
        files AS (
            SELECT
                snapshot_id,
                COALESCE(SUM(record_count), 0) AS records_added,
                COALESCE(SUM(file_size_in_bytes), 0) AS bytes_added,
                COUNT(*) AS file_count
            FROM {catalog}.{schema}."{table}$files"
            GROUP BY 1
        )
        SELECT
            s.snapshot_id,
            s.committed_at AS ds,
            COALESCE(f.records_added, CAST(s.added_records_summary AS BIGINT), 0) AS records_added,
            COALESCE(f.bytes_added, 0) AS bytes_added,
            COALESCE(f.file_count, 0) AS file_count
        FROM snapshots s
        LEFT JOIN files f ON s.snapshot_id = f.snapshot_id
        WHERE s.operation = 'append'
        ORDER BY s.committed_at
    """
    schema_query = f"""
        SELECT column_name, data_type
        FROM {catalog}.information_schema.columns
        WHERE table_schema = '{schema}' AND table_name = '{table}'
        ORDER BY ordinal_position
    """

    joined = trino_hook.get_records(joined_query)
    columns = trino_hook.get_records(schema_query)
    return {
        "joined": joined,
        "columns": columns,
    }


def persist_metrics(pg_hook: PostgresHook, table_name: str, layer: str, joined_rows: list[dict]) -> None:
    previous_ds = None
    for row in joined_rows:
        ds = datetime.fromisoformat(row["ds"])
        records_added = row["records_added"]
        bytes_added = row["bytes_added"]
        file_count = row["file_count"]
        delay = None
        if previous_ds is not None:
            delay = (ds - previous_ds).total_seconds()
        previous_ds = ds

        pg_hook.run(
            """
            INSERT INTO table_metrics (table_name, layer, ds, records_added, bytes_added, file_count, delay)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (table_name, layer, ds) DO UPDATE
            SET records_added = EXCLUDED.records_added,
                bytes_added = EXCLUDED.bytes_added,
                file_count = EXCLUDED.file_count,
                delay = EXCLUDED.delay
            """,
            parameters=(table_name, layer, ds, records_added, bytes_added, file_count, delay),
            autocommit=True,
        )


def persist_schema(pg_hook: PostgresHook, table_name: str, columns: list[dict], collected_at: datetime) -> None:
    for column in columns:
        pg_hook.run(
            """
            INSERT INTO schema_history (table_name, column_name, data_type, collected_at)
            VALUES (%s, %s, %s, %s)
            """,
            parameters=(table_name, column["column_name"], column["data_type"], collected_at),
            autocommit=True,
        )


def collect_metadata_task(**kwargs):
    ti = kwargs["ti"]
    tables = ti.xcom_pull(task_ids="collect_targets")
    if not tables:
        return []

    trino_hook = TrinoHook(trino_conn_id="trino_default")
    payload = []
    for item in tables:
        table_data = collect_table_metrics(
            trino_hook,
            catalog=item["catalog"],
            schema=item["schema"],
            table=item["table"],
        )
        payload.append(
            {
                "table_name": f"{item['schema']}.{item['table']}",
                "layer": item["layer"],
                "joined": [
                    {
                        "snapshot_id": row[0],
                        "ds": row[1].isoformat(),
                        "records_added": row[2],
                        "bytes_added": row[3],
                        "file_count": row[4],
                    }
                    for row in table_data["joined"]
                ],
                "columns": [
                    {"column_name": row[0], "data_type": row[1]}
                    for row in table_data["columns"]
                ],
            }
        )
    return payload


def save_metadata_task(**kwargs):
    ti = kwargs["ti"]
    metadata = ti.xcom_pull(task_ids="collect_metadata")
    if not metadata:
        return []

    pg_hook = PostgresHook(postgres_conn_id="datagate_db_default")
    ensure_tables(pg_hook)
    collected_at = datetime.utcnow()
    saved_tables = []

    for item in metadata:
        persist_metrics(pg_hook, item["table_name"], item["layer"], item["joined"])
        persist_schema(pg_hook, item["table_name"], item["columns"], collected_at)
        saved_tables.append(item["table_name"])

    return saved_tables


def run_prophet_task(**kwargs):
    ti = kwargs["ti"]
    tables = ti.xcom_pull(task_ids="save_metadata")
    if not tables:
        return

    backend_root = os.path.abspath("/opt/airflow/../../backend")
    if backend_root not in sys.path:
        sys.path.append(backend_root)

    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from app.services.observability_analyzer_service import ObservabilityAnalyzer
    except Exception as exc:
        logger.warning("Prophet analyzer unavailable: %s", exc)
        return

    pg_hook = PostgresHook(postgres_conn_id="datagate_db_default")
    engine = create_engine(pg_hook.get_uri())
    session = sessionmaker(bind=engine)()
    try:
        for table_name in tables:
            ObservabilityAnalyzer.analyze_table(session, table_name)
    finally:
        session.close()


with DAG(
    dag_id="data_observability",
    default_args=default_args,
    description="Collect Iceberg metadata, persist observability metrics and run Prophet",
    schedule_interval=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["datagate", "observability", "iceberg", "prophet"],
) as dag:
    collect_targets = PythonOperator(
        task_id="collect_targets",
        python_callable=get_target_tables,
        provide_context=True,
    )

    collect_metadata = PythonOperator(
        task_id="collect_metadata",
        python_callable=collect_metadata_task,
        provide_context=True,
    )

    save_metadata = PythonOperator(
        task_id="save_metadata",
        python_callable=save_metadata_task,
        provide_context=True,
    )

    run_prophet = PythonOperator(
        task_id="run_prophet",
        python_callable=run_prophet_task,
        provide_context=True,
    )

    collect_targets >> collect_metadata >> save_metadata >> run_prophet
