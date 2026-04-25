from datetime import datetime, timedelta
import pendulum

from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

LOCAL_TZ = pendulum.timezone("Asia/Ho_Chi_Minh")

default_args = {
    "owner": "datagate",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1, tzinfo=LOCAL_TZ),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

SPARK_CONF = {
    # =========================
    # Cluster
    # =========================
    "spark.master": "spark://spark-master:7077",
    "spark.submit.deployMode": "client",
    # =========================
    # Resource tuning (cluster: 10 cores / 20GB)
    # =========================
    "spark.executor.instances": "4",   # 4 executors
    "spark.executor.cores": "2",       # mỗi executor 2 cores → tổng 8 cores
    "spark.executor.memory": "4g",     # tổng ~16GB RAM
    "spark.driver.memory": "1g",

    # =========================
    # Parallelism (match job)
    # =========================
    "spark.sql.shuffle.partitions": "20",
    "spark.default.parallelism": "20",

    # =========================
    # Iceberg (bắt buộc)
    # =========================
    "spark.sql.extensions": "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
    "spark.sql.catalog.iceberg": "org.apache.iceberg.spark.SparkCatalog",
    "spark.sql.catalog.iceberg.catalog-impl": "org.apache.iceberg.rest.RESTCatalog",
    "spark.sql.catalog.iceberg.s3.path-style-access": "true",
    # =========================
    # AQE (auto optimize)
    # =========================
    "spark.sql.adaptive.enabled": "true",
    "spark.sql.adaptive.coalescePartitions.enabled": "true",

    # =========================
    # Stability
    # =========================
    "spark.network.timeout": "600s",
    "spark.executor.heartbeatInterval": "60s",
}

# JARS = ",".join(
#     [
#         "/opt/spark/jars/postgresql-42.7.10.jar",
#         "/opt/spark/jars/iceberg-spark-runtime-3.5_2.12-1.10.1.jar",
#         "/opt/spark/jars/iceberg-aws-1.10.1.jar",
#         "/opt/spark/jars/bundle-2.42.35.jar",
#     ]
# )

with DAG(
    dag_id="batch_ingestion",
    default_args=default_args,
    schedule_interval="@hourly",
    catchup=False,
    tags=["spark", "ingestion"],
) as dag:

    batch_ingestion = SparkSubmitOperator(
        task_id="batch_ingestion",
        application="/opt/airflow/dags/jobs/experiments/batch_ingestion.py", 
        conn_id="spark_default",
        deploy_mode="client", 
        conf=SPARK_CONF,

        application_args=[
            "--rest_uri", "{{ dag_run.conf.get('rest_uri', 'http://iceberg-rest:8181') }}",
            "--s3_endpoint", "{{ dag_run.conf.get('s3_endpoint', 'http://minio:9000') }}",
            "--s3_access_key", "{{ dag_run.conf.get('s3_access_key', 'admin') }}",
            "--s3_secret_key", "{{ dag_run.conf.get('s3_secret_key', 'miniopassword') }}",
            "--aws_region", "{{ dag_run.conf.get('aws_region', 'us-east-1') }}",
            "--jdbc_url", "{{ dag_run.conf.get('source_url', 'jdbc:postgresql://datasource_postgres:5432/postgres') }}",
            "--db_user", "{{ dag_run.conf.get('source_user', 'admin') }}",
            "--db_password", "{{ dag_run.conf.get('source_password', 'postgrespassword') }}",
            "--source_table", "{{ dag_run.conf.get('source_table', 'public.yellow_tripdata') }}",
            "--target_table", "{{ dag_run.conf.get('target_table', 'bronze.yellow_tripdata') }}",
            "--ingest_time", "{{ dag_run.conf.get('ingest_time', '2025-01-01 04:00:00') }}",
        ],
    )