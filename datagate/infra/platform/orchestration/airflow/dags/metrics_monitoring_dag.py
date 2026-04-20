from airflow import DAG
from datetime import datetime, timedelta


default_args = {
    "owner": "datagate_",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}
with DAG (
    dag_id="",
    default_args=default_args
)