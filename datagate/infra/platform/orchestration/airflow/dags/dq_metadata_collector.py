from datetime import datetime, timedelta

import pendulum
from airflow import DAG
from airflow.operators.python import PythonOperator

from metadata_profile_runtime import execute_metadata_profile_job

LOCAL_TZ = pendulum.timezone("Asia/Ho_Chi_Minh")
DEFAULT_DAG_ID = "dq_metadata_collector"

default_args = {
    "owner": "datagate",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1, tzinfo=LOCAL_TZ),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


def collect_metadata(**kwargs):
    dag_run = kwargs["dag_run"]
    conf = dag_run.conf or {}
    run_ts = kwargs["logical_date"].in_timezone(LOCAL_TZ).naive()

    job = {
        "job_id": conf.get("job_id", 0),
        "catalog": conf.get("catalog", "iceberg"),
        "schema_name": conf.get("schema", "public"),
        "table_name": conf.get("table"),
    }

    execute_metadata_profile_job(
        job,
        DEFAULT_DAG_ID,
        dag_run.run_id,
        conf.get("trigger_type", "manual"),
        run_ts,
    )


dag = DAG(
    DEFAULT_DAG_ID,
    default_args=default_args,
    description="On-demand metadata profiling collector",
    schedule=None,
    catchup=False,
    max_active_runs=3,
    tags=["datagate", "metadata-profile", "manual"],
)

run_task = PythonOperator(
    task_id="collect_metadata_profile",
    python_callable=collect_metadata,
    dag=dag,
)
