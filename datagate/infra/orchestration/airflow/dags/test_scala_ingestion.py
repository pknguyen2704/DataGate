from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from datetime import datetime

# ==========================================
# 1. Path & Environment Setup
# ==========================================
APPLICATION_JAR = "/opt/spark/work-dir/jobs/experiments/ingest_data-1.0.jar"
MAIN_CLASS = "datagate.experiment.batch.batch_ingestion_from_ps_to_bronze_layer"

# ==========================================
# 2. DAG Definition
# ==========================================
default_args = {
    'owner': 'datagate',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 0,
}

with DAG(
    dag_id='test_scala_ingestion_jar',
    default_args=default_args,
    description='Scala Ingestion JAR (Refined SparkSubmit)',
    schedule_interval=None,
    catchup=False,
    tags=['experiment', 'scala', 'iceberg', 'spark_submit'],
) as dag:

    submit_scala_ingestion = SparkSubmitOperator(
        task_id="submit_scala_ingestion",
        application=APPLICATION_JAR,
        java_class=MAIN_CLASS,
        conn_id="spark_default",
        verbose=False,
        conf={
            "spark.master": "spark://spark-master:7077",
            "spark.submit.deployMode": "cluster",
            "spark.driver.memory": "2g",
            "spark.executor.memory": "4g",
            "spark.executor.cores": "2"
        },
        application_args=[
            "http://iceberg-rest:8181",
            "http://minio:9000",
            "admin",
            "miniopassword",
            "us-east-1",
            "jdbc:postgresql://datasource_postgres:5432/postgres",
            "admin",
            "postgrespassword",
            "public.yellow_tripdata",
            "bronze.yellow_tripdata_scala",
            "NONE"
        ],
    )
