from datetime import timedelta

import pendulum
from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.operators.python import PythonOperator
import sys

sys.path.append("/opt/spark/jobs/datagate/pyspark")
from metadata_collection import collect_metadata

LOCAL_TZ = pendulum.timezone("Asia/Ho_Chi_Minh")

default_args = {
    "owner": "datagate",
    "depends_on_past": False,
    "start_date": pendulum.datetime(2024, 1, 1, tz=LOCAL_TZ),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


PROCESSING_DATE_HOUR = "2025-01-03 12:00:00"

JDBC_URL = "jdbc:postgresql://datasource_postgres:5432/postgres"
SOURCE_DB_USER = "admin"
SOURCE_DB_PASSWORD = "postgrespassword"

SOURCE_TABLE = "public.yellow_tripdata"

BRONZE_TABLE = "bronze.yellow_tripdata"
SILVER_TABLE = "silver.cleaned_yellow_tripdata"

GOLD_ENRICHED_TABLE = "gold.yellow_tripdata_enriched"
GOLD_TRIP_HOURLY_METRICS_TABLE = "gold.trip_hourly_metrics"
GOLD_LOCATION_HOURLY_METRICS_TABLE = "gold.location_hourly_metrics"
GOLD_PAYMENT_HOURLY_METRICS_TABLE = "gold.payment_hourly_metrics"
GOLD_VENDOR_HOURLY_METRICS_TABLE = "gold.vendor_hourly_metrics"

PYSPARK_JOB_PATH = "/opt/spark/jobs/experiments/pyspark/tlc_trip_record"
DATEGATE_JOB_PATH = "/opt/spark/jobs/datagate/pyspark"

TRINO_CONN_ID = "trino_default"
DATAGATE_DB_CONN_ID = "datagate_db_default"
DATAGATE_DB_JDBC_URL = (
    f"jdbc:postgresql://{{{{ conn.{DATAGATE_DB_CONN_ID}.host }}}}:"
    f"{{{{ conn.{DATAGATE_DB_CONN_ID}.port or 5432 }}}}/"
    f"{{{{ conn.{DATAGATE_DB_CONN_ID}.schema or 'datagate' }}}}"
)
DATAGATE_DB_USER = f"{{{{ conn.{DATAGATE_DB_CONN_ID}.login }}}}"
DATAGATE_DB_PASSWORD = f"{{{{ conn.{DATAGATE_DB_CONN_ID}.password }}}}"

METADATA_TABLES = [
    BRONZE_TABLE,
    SILVER_TABLE,
    GOLD_ENRICHED_TABLE,
    GOLD_TRIP_HOURLY_METRICS_TABLE,
    GOLD_LOCATION_HOURLY_METRICS_TABLE,
    GOLD_PAYMENT_HOURLY_METRICS_TABLE,
    GOLD_VENDOR_HOURLY_METRICS_TABLE,
]

RULE_SUGGESTION_TABLES = [
    BRONZE_TABLE,
    SILVER_TABLE,
    GOLD_ENRICHED_TABLE,
    GOLD_TRIP_HOURLY_METRICS_TABLE,
    GOLD_LOCATION_HOURLY_METRICS_TABLE,
    GOLD_PAYMENT_HOURLY_METRICS_TABLE,
    GOLD_VENDOR_HOURLY_METRICS_TABLE,
]
RULE_VERIFICATION_TABLES = RULE_SUGGESTION_TABLES
ANOMALY_TABLES = [
    BRONZE_TABLE,
    SILVER_TABLE,
    GOLD_ENRICHED_TABLE,
    GOLD_TRIP_HOURLY_METRICS_TABLE,
    GOLD_LOCATION_HOURLY_METRICS_TABLE,
    GOLD_PAYMENT_HOURLY_METRICS_TABLE,
    GOLD_VENDOR_HOURLY_METRICS_TABLE,
]
ANOMALY_TABLE_DATE_COLUMNS = {
    BRONZE_TABLE: "tpep_pickup_datetime",
    SILVER_TABLE: "tpep_pickup_datetime",
    GOLD_ENRICHED_TABLE: "tpep_pickup_datetime",
    GOLD_TRIP_HOURLY_METRICS_TABLE: "date_hour",
    GOLD_LOCATION_HOURLY_METRICS_TABLE: "date_hour",
    GOLD_PAYMENT_HOURLY_METRICS_TABLE: "date_hour",
    GOLD_VENDOR_HOURLY_METRICS_TABLE: "date_hour",
}

with DAG(
    dag_id="yellow_tripdata_pipeline",
    default_args=default_args,
    schedule=None,
    catchup=False,
    tags=["spark", "data_pipeline", "iceberg", "manual"],
) as dag:

    ingest_data = SparkSubmitOperator(
        task_id="ingest_data",
        application=f"{PYSPARK_JOB_PATH}/ingest_data.py",
        conn_id="spark_default",
        deploy_mode="client",
        application_args=[
            "--jdbc_url", JDBC_URL,
            "--source_db_user", SOURCE_DB_USER,
            "--source_db_password", SOURCE_DB_PASSWORD,
            "--source_table", SOURCE_TABLE,
            "--target_table", BRONZE_TABLE,
            "--processing_date_hour", PROCESSING_DATE_HOUR,
        ],
    )

    clean_data = SparkSubmitOperator(
        task_id="clean_data",
        application=f"{PYSPARK_JOB_PATH}/clean_data.py",
        conn_id="spark_default",
        deploy_mode="client",
        application_args=[
            "--source_table", BRONZE_TABLE,
            "--target_table", SILVER_TABLE,
            "--processing_date_hour", PROCESSING_DATE_HOUR,
        ],
    )

    transform_data = SparkSubmitOperator(
        task_id="transform_data",
        application=f"{PYSPARK_JOB_PATH}/transform_data.py",
        conn_id="spark_default",
        deploy_mode="client",
        application_args=[
            "--source_table", SILVER_TABLE,
            "--enriched_table", GOLD_ENRICHED_TABLE,
            "--trip_hourly_metrics_table", GOLD_TRIP_HOURLY_METRICS_TABLE,
            "--location_hourly_metrics_table", GOLD_LOCATION_HOURLY_METRICS_TABLE,
            "--payment_hourly_metrics_table", GOLD_PAYMENT_HOURLY_METRICS_TABLE,
            "--vendor_hourly_metrics_table", GOLD_VENDOR_HOURLY_METRICS_TABLE,
            "--processing_date_hour", PROCESSING_DATE_HOUR,
        ],
    )

    metadata_collection = PythonOperator(
        task_id="metadata_collection",
        python_callable=collect_metadata,
        op_kwargs={
            "trino_conn_id": TRINO_CONN_ID,
            "datagate_db_conn_id": DATAGATE_DB_CONN_ID,
            "table_names": METADATA_TABLES,
            "date_hour": PROCESSING_DATE_HOUR,
        },
    )

    rule_suggestion = SparkSubmitOperator(
        task_id="rule_suggestion",
        application=f"{DATEGATE_JOB_PATH}/rule_suggestion.py",
        conn_id="spark_default",
        deploy_mode="client",
        application_args=[
            "--source_tables", ",".join(RULE_SUGGESTION_TABLES),
            "--date_hour", PROCESSING_DATE_HOUR,
            "--output_format", "json",
            "--datagate_db_conn_id", DATAGATE_DB_CONN_ID,
            "--datagate_jdbc_url", DATAGATE_DB_JDBC_URL,
            "--datagate_db_user", DATAGATE_DB_USER,
            "--datagate_db_password", DATAGATE_DB_PASSWORD,
        ],
    )
    # rule_verification = SparkSubmitOperator(
    #     task_id="rule_verification",
    #     application=f"{DATEGATE_JOB_PATH}/rule_verification.py",
    #     conn_id="spark_default",
    #     deploy_mode="client",
    #     application_args=[
    #         "--source_tables", ",".join(RULE_VERIFICATION_TABLES),
    #         "--date_hour", PROCESSING_DATE_HOUR,
    #         "--output_format", "json",
    #         "--datagate_db_conn_id", DATAGATE_DB_CONN_ID,
    #         "--datagate_jdbc_url", DATAGATE_DB_JDBC_URL,
    #         "--datagate_db_user", DATAGATE_DB_USER,
    #         "--datagate_db_password", DATAGATE_DB_PASSWORD,
    #     ],
    # )

    anomaly_detection = SparkSubmitOperator(
        task_id="anomaly_detection",
        application=f"{DATEGATE_JOB_PATH}/anomaly_detection.py",
        conn_id="spark_default",
        deploy_mode="client",
        application_args=[
            "--source_tables", ",".join(ANOMALY_TABLES),
            "--table_date_columns", ",".join(
                f"{table_name}={date_column}"
                for table_name, date_column in ANOMALY_TABLE_DATE_COLUMNS.items()
            ),
            "--date_hour", PROCESSING_DATE_HOUR,
            "--output_format", "json",
            "--datagate_db_conn_id", DATAGATE_DB_CONN_ID,
            "--datagate_jdbc_url", DATAGATE_DB_JDBC_URL,
            "--datagate_db_user", DATAGATE_DB_USER,
            "--datagate_db_password", DATAGATE_DB_PASSWORD,
        ],
    )

    ingest_data >> clean_data >> transform_data >> metadata_collection >> rule_suggestion >> anomaly_detection
