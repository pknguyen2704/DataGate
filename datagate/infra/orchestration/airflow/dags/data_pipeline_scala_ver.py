from datetime import timedelta
import pendulum

from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

LOCAL_TZ = pendulum.timezone("Asia/Ho_Chi_Minh")

default_args = {
    "owner": "datagate",
    "depends_on_past": False,
    "start_date": pendulum.datetime(2024, 1, 1, tz=LOCAL_TZ),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="data_pipeline_scala_ver",
    default_args=default_args,
    schedule="@hourly",
    catchup=False,
    tags=["spark", "data_pipeline", "iceberg"],
) as dag:

    batch_ingestion = SparkSubmitOperator(
        task_id="batch_ingestion",
        application="/opt/spark/jobs/experiments/ingestion-1.0.jar",
        java_class="ingest_data",
        conn_id="spark_default",
        deploy_mode="client",

        application_args=[
            "--jdbc_url", "jdbc:postgresql://datasource_postgres:5432/postgres",
            "--source_db_user", "admin",
            "--source_db_password", "postgrespassword",
            "--source_table", "public.yellow_tripdata",
            "--target_table", "bronze.yellow_tripdata",
            "--ingestion_time", "2025-01-01 00:00:00",
        ],
    )