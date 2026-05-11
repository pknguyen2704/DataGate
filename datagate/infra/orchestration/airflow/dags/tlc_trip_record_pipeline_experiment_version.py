from datetime import datetime, timedelta
import sys

import pendulum
from airflow import DAG
from airflow.exceptions import AirflowSkipException
from airflow.models import Variable
from airflow.operators.python import PythonOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.providers.slack.notifications.slack_webhook import send_slack_webhook_notification
sys.path.append("/opt/spark/jobs/datagate")

from batch_metadata_collection_job import collect_metadata
from batch_metadata_metrics_verify import evaluate_metadata_metrics
from batch_profiling_metrics_verify import evaluate_profiling_metrics
from data_quality_gate import check_data_quality_gate
LOCAL_TZ = pendulum.timezone("Asia/Ho_Chi_Minh")


SIM_START = "2025-01-28 12:00:00"
SIM_END = "2025-02-01 00:00:00"
SIM_STEP_HOURS = 12
SIM_VAR_NAME = "yellow_tripdata_next_processing_date_hour"


PYSPARK_JOB_PATH = "/opt/spark/jobs/experiments/tlc_trip_record"
DATAGATE_JOB_PATH = "/opt/spark/jobs/datagate"
PROCESSING_DATE_HOUR = "{{ ti.xcom_pull(task_ids='get_processing_date_hour') }}"

CONNECTION_NAME = "my lakehouse"
TRINO_CONN_ID = "trino_default"
DATAGATE_DB_CONN_ID = "datagate_db_default"
SLACK_AIRFLOW_FAILURES_CONN_ID = "slack_airflow_failures"
SLACK_DQ_CONN_ID = "slack_dq"

task_fail_slack_alert = send_slack_webhook_notification(
    slack_webhook_conn_id=SLACK_AIRFLOW_FAILURES_CONN_ID,
    text="\n".join([
        ":red_circle: *Data Pipeline Failed*",
        "",
        "*Status*: `FAILED`",
        "*DAG*: `{{ dag.dag_id }}`",
        "*Task*: `{{ ti.task_id }}`",
        "*Run ID*: `{{ run_id }}`",
        "*Try*: `{{ ti.try_number }}`",
        "*Execution Time*: `{{ ts }}`",
        "*Processing Date Hour*: `{{ dag_run.conf.get('processing_date_hour', params.processing_date_hour) if dag_run else params.processing_date_hour }}`",
        "",
        "*Log*: <{{ ti.log_url }}|Open task log>",
    ]),
)

default_args = {
    "owner": "datagate",
    "depends_on_past": False,
    "start_date": pendulum.datetime(2024, 1, 1, tz=LOCAL_TZ),
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
    "on_failure_callback": [task_fail_slack_alert],
}


def get_processing_date_hour():
    value = Variable.get(SIM_VAR_NAME, default_var=SIM_START)
    current_dt = datetime.fromisoformat(value)
    end_dt = datetime.fromisoformat(SIM_END)

    if current_dt > end_dt:
        raise AirflowSkipException(
            f"Simulation completed. current={value}, end={SIM_END}"
        )

    return current_dt.strftime("%Y-%m-%d %H:%M:%S")


def advance_processing_date_hour(ti):
    current_value = ti.xcom_pull(task_ids="get_processing_date_hour")
    next_dt = datetime.fromisoformat(current_value) + timedelta(hours=SIM_STEP_HOURS)
    Variable.set(SIM_VAR_NAME, next_dt.strftime("%Y-%m-%d %H:%M:%S"))


with DAG(
    dag_id="yellow_tripdata_pipeline_experiment_version",
    default_args=default_args,
    schedule=timedelta(minutes=10),
    catchup=False,
    max_active_runs=1,
    is_paused_upon_creation=True,
    tags=["datagate", "iceberg", "yellow_tripdata", "simulation"],
) as dag:

    get_processing_date_hour_task = PythonOperator(
        task_id="get_processing_date_hour",
        python_callable=get_processing_date_hour,
    )

    advance_processing_date_hour_task = PythonOperator(
        task_id="advance_processing_date_hour",
        python_callable=advance_processing_date_hour,
    )

    ingest_data = SparkSubmitOperator(
        task_id="ingest_data",
        application=f"{PYSPARK_JOB_PATH}/ingest_data.py",
        conn_id="spark_default",
        deploy_mode="client",
        application_args=[
            "--processing_date_hour", PROCESSING_DATE_HOUR,
        ],
    )

    bronze_tables_metadata_collection = PythonOperator(
        task_id="bronze_tables_metadata_collection",
        python_callable=collect_metadata,
        op_kwargs={
            "trino_conn_id": TRINO_CONN_ID,
            "datagate_db_conn_id": DATAGATE_DB_CONN_ID,
            "connection_name": CONNECTION_NAME,
            "schema_name": "bronze",
            "processing_date_hour": PROCESSING_DATE_HOUR,
        },
    )

    bronze_tables_profiling_collection = SparkSubmitOperator(
        task_id="bronze_tables_profiling_collection",
        application=f"{DATAGATE_JOB_PATH}/batch_profiling_collection_job.py",
        conn_id="spark_default",
        deploy_mode="client",
        application_args=[
            "--datagate_db_conn_id", DATAGATE_DB_CONN_ID,
            "--connection_name", CONNECTION_NAME,
            "--schema_name", "bronze",
            "--processing_date_hour", PROCESSING_DATE_HOUR,
        ],
    )

    bronze_tables_metadata_metrics_verify = PythonOperator(
        task_id="bronze_tables_metadata_metrics_verify",
        python_callable=evaluate_metadata_metrics,
        op_kwargs={
            "datagate_db_conn_id": DATAGATE_DB_CONN_ID,
            "connection_name": CONNECTION_NAME,
            "schema_name": "bronze",
            "processing_date_hour": PROCESSING_DATE_HOUR,
        },
    )
    
    bronze_tables_profiling_metrics_verify = PythonOperator(
        task_id="bronze_tables_profiling_metrics_verify",
        python_callable=evaluate_profiling_metrics,
        op_kwargs={
            "datagate_db_conn_id": DATAGATE_DB_CONN_ID,
            "connection_name": CONNECTION_NAME,
            "schema_name": "bronze",
            "processing_date_hour": PROCESSING_DATE_HOUR,
        },
    )

    bronze_data_quality_gate = PythonOperator(
        task_id="bronze_data_quality_gate",
        python_callable=check_data_quality_gate,
        retries=0,
        op_kwargs={
            "datagate_db_conn_id": DATAGATE_DB_CONN_ID,
            "connection_name": CONNECTION_NAME,
            "schema_name": "bronze",
            "processing_date_hour": PROCESSING_DATE_HOUR,
            "slack_webhook_conn_id": SLACK_DQ_CONN_ID,
        },
    )

    clean_data = SparkSubmitOperator(
        task_id="clean_data",
        application=f"{PYSPARK_JOB_PATH}/clean_data.py",
        conn_id="spark_default",
        deploy_mode="client",
        application_args=[
            "--processing_date_hour", PROCESSING_DATE_HOUR,
        ],
    )

    silver_tables_metadata_collection = PythonOperator(
        task_id="silver_tables_metadata_collection",
        python_callable=collect_metadata,
        op_kwargs={
            "trino_conn_id": TRINO_CONN_ID,
            "datagate_db_conn_id": DATAGATE_DB_CONN_ID,
            "connection_name": CONNECTION_NAME,
            "schema_name": "silver",
            "processing_date_hour": PROCESSING_DATE_HOUR,
        },
    )

    silver_tables_profiling_collection = SparkSubmitOperator(
        task_id="silver_tables_profiling_collection",
        application=f"{DATAGATE_JOB_PATH}/batch_profiling_collection_job.py",
        conn_id="spark_default",
        deploy_mode="client",
        application_args=[
            "--datagate_db_conn_id", DATAGATE_DB_CONN_ID,
            "--connection_name", CONNECTION_NAME,
            "--schema_name", "silver",
            "--processing_date_hour", PROCESSING_DATE_HOUR,
        ],
    )

    silver_tables_metadata_metrics_verify = PythonOperator(
        task_id="silver_tables_metadata_metrics_verify",
        python_callable=evaluate_metadata_metrics,
        op_kwargs={
            "datagate_db_conn_id": DATAGATE_DB_CONN_ID,
            "connection_name": CONNECTION_NAME,
            "schema_name": "silver",
            "processing_date_hour": PROCESSING_DATE_HOUR,
        },
    )

    silver_tables_profiling_metrics_verify = PythonOperator(
        task_id="silver_tables_profiling_metrics_verify",
        python_callable=evaluate_profiling_metrics,
        op_kwargs={
            "datagate_db_conn_id": DATAGATE_DB_CONN_ID,
            "connection_name": CONNECTION_NAME,
            "schema_name": "silver",
            "processing_date_hour": PROCESSING_DATE_HOUR,
        },
    )

    silver_batch_rule_verification = SparkSubmitOperator(
        task_id="silver_batch_rule_verification",
        application=f"{DATAGATE_JOB_PATH}/batch_rule_verification.py",
        conn_id="spark_default",
        deploy_mode="client",
        application_args=[
            "--datagate_db_conn_id", DATAGATE_DB_CONN_ID,
            "--connection_name", CONNECTION_NAME,
            "--schema_name", "silver",
            "--processing_date_hour", PROCESSING_DATE_HOUR,
        ],
    )

    silver_batch_anomaly_detection_tlc_trip_record = SparkSubmitOperator(
        task_id="silver_batch_anomaly_detection_tlc_trip_record",
        application=f"{DATAGATE_JOB_PATH}/batch_anomaly_detection_tlc_trip_record.py",
        conn_id="spark_default",
        deploy_mode="client",
        application_args=[
            "--datagate_db_conn_id", DATAGATE_DB_CONN_ID,
            "--connection_name", CONNECTION_NAME,
            "--schema_name", "silver",
            "--processing_date_hour", PROCESSING_DATE_HOUR,
        ],
    )

    silver_data_quality_gate = PythonOperator(
        task_id="silver_data_quality_gate",
        python_callable=check_data_quality_gate,
        retries=0,
        op_kwargs={
            "datagate_db_conn_id": DATAGATE_DB_CONN_ID,
            "connection_name": CONNECTION_NAME,
            "schema_name": "silver",
            "processing_date_hour": PROCESSING_DATE_HOUR,
            "slack_webhook_conn_id": SLACK_DQ_CONN_ID,
        },
    )

    transform_data = SparkSubmitOperator(
        task_id="transform_data",
        application=f"{PYSPARK_JOB_PATH}/transform_data.py",
        conn_id="spark_default",
        deploy_mode="client",
        application_args=[
            "--processing_date_hour", PROCESSING_DATE_HOUR,
        ],
    )

    gold_tables_metadata_collection = PythonOperator(
        task_id="gold_tables_metadata_collection",
        python_callable=collect_metadata,
        op_kwargs={
            "trino_conn_id": TRINO_CONN_ID,
            "datagate_db_conn_id": DATAGATE_DB_CONN_ID,
            "connection_name": CONNECTION_NAME,
            "schema_name": "gold",
            "processing_date_hour": PROCESSING_DATE_HOUR,
        },
    )

    gold_tables_profiling_collection = SparkSubmitOperator(
        task_id="gold_tables_profiling_collection",
        application=f"{DATAGATE_JOB_PATH}/batch_profiling_collection_job.py",
        conn_id="spark_default",
        deploy_mode="client",
        application_args=[
            "--datagate_db_conn_id", DATAGATE_DB_CONN_ID,
            "--connection_name", CONNECTION_NAME,
            "--schema_name", "gold",
            "--processing_date_hour", PROCESSING_DATE_HOUR,
        ],
    )

    gold_tables_metadata_metrics_verify = PythonOperator(
        task_id="gold_tables_metadata_metrics_verify",
        python_callable=evaluate_metadata_metrics,
        op_kwargs={
            "datagate_db_conn_id": DATAGATE_DB_CONN_ID,
            "connection_name": CONNECTION_NAME,
            "schema_name": "gold",
            "processing_date_hour": PROCESSING_DATE_HOUR,
        },
    )

    gold_tables_profiling_metrics_verify = PythonOperator(
        task_id="gold_tables_profiling_metrics_verify",
        python_callable=evaluate_profiling_metrics,
        op_kwargs={
            "datagate_db_conn_id": DATAGATE_DB_CONN_ID,
            "connection_name": CONNECTION_NAME,
            "schema_name": "gold",
            "processing_date_hour": PROCESSING_DATE_HOUR,
        },
    )

    gold_batch_rule_verification = SparkSubmitOperator(
        task_id="gold_batch_rule_verification",
        application=f"{DATAGATE_JOB_PATH}/batch_rule_verification.py",
        conn_id="spark_default",
        deploy_mode="client",
        application_args=[
            "--datagate_db_conn_id", DATAGATE_DB_CONN_ID,
            "--connection_name", CONNECTION_NAME,
            "--schema_name", "gold",
            "--processing_date_hour", PROCESSING_DATE_HOUR,
        ],
    )

    gold_data_quality_gate = PythonOperator(
        task_id="gold_data_quality_gate",
        python_callable=check_data_quality_gate,
        retries=0,
        op_kwargs={
            "datagate_db_conn_id": DATAGATE_DB_CONN_ID,
            "connection_name": CONNECTION_NAME,
            "schema_name": "gold",
            "processing_date_hour": PROCESSING_DATE_HOUR,
            "slack_webhook_conn_id": SLACK_DQ_CONN_ID,
        },
    )

    batch_rule_suggestion = SparkSubmitOperator(
        task_id="batch_rule_suggestion",
        application=f"{DATAGATE_JOB_PATH}/batch_rule_suggestion.py",
        conn_id="spark_default",
        deploy_mode="client",
        application_args=[
            "--datagate_db_conn_id", DATAGATE_DB_CONN_ID,
            "--connection_name", CONNECTION_NAME,
            "--schema_names", "silver", "gold",
            "--processing_date_hour", PROCESSING_DATE_HOUR,
        ],
    )


    get_processing_date_hour_task >> ingest_data

    # ----------------------------
    # Bronze layer
    # ----------------------------
    ingest_data >> [
        bronze_tables_metadata_collection,
        bronze_tables_profiling_collection
    ]
    bronze_tables_metadata_collection >>  bronze_tables_metadata_metrics_verify
    bronze_tables_profiling_collection >> bronze_tables_profiling_metrics_verify
    [
        bronze_tables_metadata_metrics_verify,
        bronze_tables_profiling_metrics_verify
    ] >> bronze_data_quality_gate >> clean_data

    # ----------------------------
    # Silver layer
    # ----------------------------
    clean_data >> [
        silver_tables_metadata_collection,
        silver_tables_profiling_collection,
    ] 

    silver_tables_metadata_collection >> silver_tables_metadata_metrics_verify
    silver_tables_profiling_collection >> silver_tables_profiling_metrics_verify

    [
        silver_tables_metadata_metrics_verify,
        silver_tables_profiling_metrics_verify,
    ] >> silver_batch_rule_verification >> silver_batch_anomaly_detection_tlc_trip_record >> silver_data_quality_gate >> transform_data

    # ----------------------------
    # Gold layer
    # ----------------------------
    transform_data >> [
        gold_tables_metadata_collection,
        gold_tables_profiling_collection,
    ] 
    gold_tables_metadata_collection >> gold_tables_metadata_metrics_verify
    gold_tables_profiling_collection >> gold_tables_profiling_metrics_verify
    [
        gold_tables_metadata_metrics_verify,
        gold_tables_profiling_metrics_verify,
    ] >> gold_batch_rule_verification >> gold_data_quality_gate >> batch_rule_suggestion >> advance_processing_date_hour_task