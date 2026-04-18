from datetime import datetime, timedelta
import pendulum
import os
from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

# Configuration
LOCAL_TZ = pendulum.timezone("Asia/Ho_Chi_Minh")
DEFAULT_DAG_ID = "load_data_from_datasource"

default_args = {
    "owner": "datagate",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1, tzinfo=LOCAL_TZ),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    DEFAULT_DAG_ID,
    default_args=default_args,
    description="Ingest data from datasource using PySpark",
    schedule_interval=None,
    catchup=False,
    tags=["datagate", "ingestion", "spark"],
)

# Path to the script that both Airflow and Spark Workers can see
JOB_SCRIPT_PATH = "/opt/spark/jobs/experiments/batch_ingestion.py"

submit_pyspark_ingestion = SparkSubmitOperator(
    task_id="submit_pyspark_ingestion",
    application=JOB_SCRIPT_PATH,
    conn_id="spark_default",
    # Chế độ client là bắt buộc cho PySpark trên Standalone Cluster
    deploy_mode="client",
    # Ở chế độ client, Driver (Airflow) cần nhìn thấy các JAR này
    jars="/opt/spark/jars/postgresql-42.7.10.jar,"
         "/opt/spark/jars/iceberg-spark-runtime-3.5_2.12-1.10.1.jar,"
         "/opt/spark/jars/iceberg-aws-1.10.1.jar,"
         "/opt/spark/jars/bundle-2.42.35.jar,"
         "/opt/spark/jars/deequ-2.0.16-spark-3.5.jar",
    verbose=False,
    conf={
        "spark.master": "spark://spark-master:7077",
        "spark.driver.memory": "2g",
        "spark.executor.memory": "4g",
        "spark.executor.cores": "2",
        "spark.driver.extraJavaOptions": "-Daws.region=us-east-1",
        "spark.executor.extraJavaOptions": "-Daws.region=us-east-1",
        # Tăng cấu hình mạng để xử lý JAR lớn và Iceberg metadata
        "spark.rpc.message.maxSize": "1024",
        "spark.network.timeout": "800s",
        "spark.sql.catalog.iceberg": "org.apache.iceberg.spark.SparkCatalog",
        "spark.sql.catalog.iceberg.catalog-impl": "org.apache.iceberg.rest.RESTCatalog",
        "spark.sql.catalog.iceberg.uri": "http://iceberg-rest:8181",
        "spark.sql.catalog.iceberg.warehouse": "s3://lakehouse/",
        "spark.sql.catalog.iceberg.io-impl": "org.apache.iceberg.aws.s3.S3FileIO",
        "spark.sql.catalog.iceberg.s3.endpoint": "http://minio:9000",
        "spark.sql.catalog.iceberg.s3.path-style-access": "true",
        "spark.sql.catalog.iceberg.s3.access-key-id": "admin",
        "spark.sql.catalog.iceberg.s3.secret-access-key": "miniopassword",
        "spark.sql.catalog.iceberg.s3.region": "us-east-1",
    },
    application_args=[
        "{{ dag_run.conf.get('rest_uri', 'http://iceberg-rest:8181') }}",
        "{{ dag_run.conf.get('s3_endpoint', 'http://minio:9000') }}",
        "{{ dag_run.conf.get('s3_access_key', 'admin') }}",
        "{{ dag_run.conf.get('s3_secret_key', 'miniopassword') }}",
        "{{ dag_run.conf.get('aws_region', 'us-east-1') }}",
        "{{ dag_run.conf.get('source_url', 'jdbc:postgresql://datasource_postgres:5432/postgres') }}",
        "{{ dag_run.conf.get('source_user', 'admin') }}",
        "{{ dag_run.conf.get('source_password', 'postgrespassword') }}",
        "{{ dag_run.conf.get('source_table', 'public.yellow_tripdata') }}",
        "{{ dag_run.conf.get('target_table', 'bronze.yellow_tripdata') }}",
        "{{ dag_run.conf.get('ingest_time', 'NONE') }}",
        "{{ dag_run.conf.get('batch_interval', '60') }}"
    ],
    dag=dag,
)

submit_pyspark_ingestion
