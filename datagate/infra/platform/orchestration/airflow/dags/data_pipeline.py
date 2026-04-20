from datetime import datetime, timedelta

import pendulum
from airflow import DAG
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

LOCAL_TZ = pendulum.timezone("Asia/Ho_Chi_Minh")
DEFAULT_DAG_ID = "data_pipeline"

SPARK_JARS = ",".join(
    [
        "/opt/spark/jars/postgresql-42.7.10.jar",
        "/opt/spark/jars/iceberg-spark-runtime-3.5_2.12-1.10.1.jar",
        "/opt/spark/jars/iceberg-aws-1.10.1.jar",
        "/opt/spark/jars/bundle-2.42.35.jar",
        "/opt/spark/jars/deequ-2.0.16-spark-3.5.jar",
    ]
)

SPARK_CONF = {
    "spark.master": "spark://spark-master:7077",
    "spark.driver.memory": "2g",
    "spark.executor.memory": "4g",
    "spark.executor.cores": "2",
    "spark.driver.extraJavaOptions": "-Daws.region=us-east-1",
    "spark.executor.extraJavaOptions": "-Daws.region=us-east-1",
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
}

default_args = {
    "owner": "datagate",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1, tzinfo=LOCAL_TZ),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


def build_spark_task(task_id: str, script_name: str, application_args: list[str], dag: DAG) -> SparkSubmitOperator:
    return SparkSubmitOperator(
        task_id=task_id,
        application=f"/opt/spark/jobs/experiments/{script_name}",
        conn_id="spark_default",
        deploy_mode="client",
        jars=SPARK_JARS,
        verbose=False,
        conf=SPARK_CONF,
        application_args=application_args,
        dag=dag,
    )


dag = DAG(
    DEFAULT_DAG_ID,
    default_args=default_args,
    description="Medallion data pipeline and trigger metadata observability",
    schedule_interval="@hourly",
    catchup=False,
    tags=["datagate", "pipeline", "medallion", "spark"],
)

batch_ingestion = build_spark_task(
    task_id="batch_ingestion",
    script_name="batch_ingestion.py",
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
        "{{ dag_run.conf.get('raw_table', 'bronze.yellow_tripdata') }}",
        "{{ dag_run.conf.get('ingest_time', 'NONE') }}",
        "{{ dag_run.conf.get('batch_interval', '60') }}",
    ],
    dag=dag,
)

# clean_data = build_spark_task(
#     task_id="clean_data",
#     script_name="clean_data.py",
#     application_args=[
#         "{{ dag_run.conf.get('rest_uri', 'http://iceberg-rest:8181') }}",
#         "{{ dag_run.conf.get('s3_endpoint', 'http://minio:9000') }}",
#         "{{ dag_run.conf.get('s3_access_key', 'admin') }}",
#         "{{ dag_run.conf.get('s3_secret_key', 'miniopassword') }}",
#         "{{ dag_run.conf.get('aws_region', 'us-east-1') }}",
#         "{{ dag_run.conf.get('raw_table', 'bronze_raw.yellow_tripdata') }}",
#         "{{ dag_run.conf.get('bronze_table', 'bronze.yellow_tripdata') }}",
#     ],
#     dag=dag,
# )

# transform = build_spark_task(
#     task_id="transform",
#     script_name="transform.py",
#     application_args=[
#         "{{ dag_run.conf.get('rest_uri', 'http://iceberg-rest:8181') }}",
#         "{{ dag_run.conf.get('s3_endpoint', 'http://minio:9000') }}",
#         "{{ dag_run.conf.get('s3_access_key', 'admin') }}",
#         "{{ dag_run.conf.get('s3_secret_key', 'miniopassword') }}",
#         "{{ dag_run.conf.get('aws_region', 'us-east-1') }}",
#         "{{ dag_run.conf.get('bronze_table', 'bronze.yellow_tripdata') }}",
#         "{{ dag_run.conf.get('silver_table', 'silver.yellow_tripdata') }}",
#         "{{ dag_run.conf.get('gold_table', 'gold.yellow_trip_summary') }}",
#     ],
#     dag=dag,
# )

# trigger_observability = TriggerDagRunOperator(
#     task_id="trigger_observability",
#     trigger_dag_id="data_observability",
#     wait_for_completion=False,
#     reset_dag_run=False,
#     conf={
#         "catalog": "{{ dag_run.conf.get('catalog', 'iceberg') }}",
#         "tables": [
#             {"layer": "bronze", "schema": "bronze", "table": "{{ dag_run.conf.get('bronze_table', 'bronze.yellow_tripdata').split('.')[1] }}"},
#             {"layer": "silver", "schema": "silver", "table": "{{ dag_run.conf.get('silver_table', 'silver.yellow_tripdata').split('.')[1] }}"},
#             {"layer": "gold", "schema": "gold", "table": "{{ dag_run.conf.get('gold_table', 'gold.yellow_trip_summary').split('.')[1] }}"},
#         ],
#     },
#     dag=dag,
# )

batch_ingestion 
# >> clean_data >> transform >> trigger_observability
