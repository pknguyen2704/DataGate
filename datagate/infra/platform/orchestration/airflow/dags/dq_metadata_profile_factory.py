from datetime import datetime, timedelta
import json
from pathlib import Path

import pendulum
from airflow import DAG
from airflow.operators.python import PythonOperator

from metadata_profile_runtime import execute_metadata_profile_job

LOCAL_TZ = pendulum.timezone("Asia/Ho_Chi_Minh")
BASE_DIR = Path(__file__).resolve().parent
GENERATED_CONFIGS_DIR = BASE_DIR / "generated_configs"

default_args = {
    "owner": "datagate",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1, tzinfo=LOCAL_TZ),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


def resolve_schedule(job_config):
    if not job_config.get("is_active", True):
        return None

    schedule_type = (job_config.get("schedule_type") or "daily").lower()
    if schedule_type == "interval":
        interval_minutes = int(job_config.get("interval_minutes") or 0)
        return timedelta(minutes=interval_minutes) if interval_minutes > 0 else None

    hour = job_config.get("hour")
    minute = job_config.get("minute")
    if hour is None or minute is None:
        return None
    return f"{int(minute)} {int(hour)} * * *"


def build_dag(job_config):
    dag_id = job_config["dag_id"]
    schedule = resolve_schedule(job_config)

    def _run(**kwargs):
      dag_run = kwargs["dag_run"]
      run_ts = kwargs["logical_date"].in_timezone(LOCAL_TZ).naive()
      conf = dag_run.conf or {}

      effective_job = {
          "job_id": job_config["job_id"],
          "catalog": conf.get("catalog", job_config.get("catalog", "iceberg")),
          "schema_name": conf.get("schema", job_config.get("schema_name", "public")),
          "table_name": conf.get("table", job_config.get("table_name")),
      }

      execute_metadata_profile_job(
          effective_job,
          dag_id,
          dag_run.run_id,
          conf.get("trigger_type", "scheduled"),
          run_ts,
      )

    dag = DAG(
        dag_id,
        default_args=default_args,
        description=f"Metadata profile DAG for {job_config.get('table_name')}",
        schedule=schedule,
        catchup=False,
        max_active_runs=3,
        tags=["datagate", "metadata-profile", "generated"],
    )

    PythonOperator(
        task_id="collect_metadata_profile",
        python_callable=_run,
        dag=dag,
    )

    return dag


if GENERATED_CONFIGS_DIR.exists():
    for config_file in GENERATED_CONFIGS_DIR.glob("*.json"):
        job_config = json.loads(config_file.read_text(encoding="utf-8"))
        generated_dag = build_dag(job_config)
        globals()[generated_dag.dag_id] = generated_dag
