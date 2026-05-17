from datetime import timedelta

import pendulum
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.providers.slack.notifications.slack_webhook import send_slack_webhook_notification

from datagate import datagate_job_path
from datagate.batch_metadata_collection_job import collect_metadata
from datagate.batch_metadata_metrics_verify import evaluate_metadata_metrics
from datagate.batch_profiling_metrics_verify import evaluate_profiling_metrics
from datagate.data_quality_gate import check_data_quality_gate


LOCAL_TZ = pendulum.timezone("Asia/Ho_Chi_Minh")
PROCESSING_DATE_HOUR = "{{ dag_run.conf.get('processing_date_hour', params.processing_date_hour) }}"

CONNECTION_NAME = "my lakehouse"
TRINO_CONN_ID = "trino_default"
DATAGATE_DB_CONN_ID = "datagate_db_default"
SLACK_AIRFLOW_FAILURES_CONN_ID = "slack_airflow_failures"
SLACK_DQ_CONN_ID = "slack_dq"
PYSPARK_JOB_PATH = "/opt/airflow/etl/citi_bike_tripdata"

DATAGATE_SPARK_CONF = {
    "spark.driver.cores": "2",
    "spark.driver.memory": "4g",
    "spark.executor.instances": "2",
    "spark.executor.cores": "6",
    "spark.executor.memory": "10g",
    "spark.sql.session.timeZone": "Asia/Ho_Chi_Minh",
    "spark.sql.shuffle.partitions": "24",
    "spark.default.parallelism": "24",
    "spark.serializer": "org.apache.spark.serializer.KryoSerializer",
}

DATAGATE_ANOMALY_SPARK_CONF = {
    **DATAGATE_SPARK_CONF,
    "spark.task.cpus": "3",
    "spark.dynamicAllocation.enabled": "false",
    "spark.speculation": "false",
    "spark.scheduler.mode": "FIFO",
    "spark.executorEnv.OMP_NUM_THREADS": "3",
    "spark.executorEnv.MKL_NUM_THREADS": "1",
    "spark.executorEnv.OPENBLAS_NUM_THREADS": "1",
    "spark.executorEnv.NUMEXPR_NUM_THREADS": "1",
}

DATAGATE_ANOMALY_JOB_ARGS = [
    "--lgbm-use-barrier-execution-mode", "true",
    "--lgbm-num-tasks", "4",
    "--lgbm-num-threads", "3",
    "--lgbm-timeout", "1200",
    "--lgbm-use-single-dataset-mode", "true",
    "--lgbm-data-transfer-mode", "streaming",
    "--lgbm-verbosity", "-1",
    "--spark-cleanup-timeout-seconds", "30",
    "--py4j-cleanup-timeout-seconds", "5",
    "--db-cleanup-timeout-seconds", "10",
]

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
    "start_date": pendulum.datetime(2025, 1, 1, tz=LOCAL_TZ),
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
    "execution_timeout": timedelta(hours=2),
    "on_failure_callback": [task_fail_slack_alert],
}


def metadata_tasks(schema_name):
    metadata = PythonOperator(
        task_id=f"{schema_name}_tables_metadata_collection",
        python_callable=collect_metadata,
        op_kwargs={
            "trino_conn_id": TRINO_CONN_ID,
            "datagate_db_conn_id": DATAGATE_DB_CONN_ID,
            "connection_name": CONNECTION_NAME,
            "schema_name": schema_name,
            "processing_date_hour": PROCESSING_DATE_HOUR,
        },
    )
    profiling = SparkSubmitOperator(
        task_id=f"{schema_name}_tables_profiling_collection",
        application=datagate_job_path("profiling_collection"),
        conn_id="spark_default",
        deploy_mode="client",
        conf=DATAGATE_SPARK_CONF,
        application_args=[
            "--datagate_db_conn_id", DATAGATE_DB_CONN_ID,
            "--connection_name", CONNECTION_NAME,
            "--schema_name", schema_name,
            "--processing_date_hour", PROCESSING_DATE_HOUR,
        ],
    )
    metadata_verify = PythonOperator(
        task_id=f"{schema_name}_tables_metadata_metrics_verify",
        python_callable=evaluate_metadata_metrics,
        op_kwargs={
            "datagate_db_conn_id": DATAGATE_DB_CONN_ID,
            "connection_name": CONNECTION_NAME,
            "schema_name": schema_name,
            "processing_date_hour": PROCESSING_DATE_HOUR,
        },
    )
    profiling_verify = PythonOperator(
        task_id=f"{schema_name}_tables_profiling_metrics_verify",
        python_callable=evaluate_profiling_metrics,
        op_kwargs={
            "datagate_db_conn_id": DATAGATE_DB_CONN_ID,
            "connection_name": CONNECTION_NAME,
            "schema_name": schema_name,
            "processing_date_hour": PROCESSING_DATE_HOUR,
        },
    )
    gate = PythonOperator(
        task_id=f"{schema_name}_data_quality_gate",
        python_callable=check_data_quality_gate,
        retries=0,
        op_kwargs={
            "datagate_db_conn_id": DATAGATE_DB_CONN_ID,
            "connection_name": CONNECTION_NAME,
            "schema_name": schema_name,
            "processing_date_hour": PROCESSING_DATE_HOUR,
            "slack_webhook_conn_id": SLACK_DQ_CONN_ID,
        },
    )
    return metadata, profiling, metadata_verify, profiling_verify, gate


with DAG(
    dag_id="citi_bike_tripdata_pipeline",
    default_args=default_args,
    schedule=None,
    dagrun_timeout=timedelta(hours=6),
    catchup=False,
    tags=["datagate", "iceberg", "citi_bike_tripdata"],
    params={"processing_date_hour": "2025-01-01 12:00:00"},
) as dag:
    ingest_data = SparkSubmitOperator(
        task_id="ingest_data",
        application=f"{PYSPARK_JOB_PATH}/ingest_data.py",
        conn_id="spark_default",
        deploy_mode="client",
        application_args=["--processing_date_hour", PROCESSING_DATE_HOUR],
    )

    clean_data = SparkSubmitOperator(
        task_id="clean_data",
        application=f"{PYSPARK_JOB_PATH}/clean_data.py",
        conn_id="spark_default",
        deploy_mode="client",
        application_args=["--processing_date_hour", PROCESSING_DATE_HOUR],
    )

    transform_data = SparkSubmitOperator(
        task_id="transform_data",
        application=f"{PYSPARK_JOB_PATH}/transform_data.py",
        conn_id="spark_default",
        deploy_mode="client",
        application_args=["--processing_date_hour", PROCESSING_DATE_HOUR],
    )

    bronze_meta, bronze_profile, bronze_meta_verify, bronze_profile_verify, bronze_gate = metadata_tasks("bronze")
    silver_meta, silver_profile, silver_meta_verify, silver_profile_verify, silver_gate = metadata_tasks("silver")
    gold_meta, gold_profile, gold_meta_verify, gold_profile_verify, gold_gate = metadata_tasks("gold")

    silver_rule_verification = SparkSubmitOperator(
        task_id="silver_batch_rule_verification",
        application=datagate_job_path("rule_verification"),
        conn_id="spark_default",
        deploy_mode="client",
        conf=DATAGATE_SPARK_CONF,
        application_args=[
            "--datagate_db_conn_id", DATAGATE_DB_CONN_ID,
            "--connection_name", CONNECTION_NAME,
            "--schema_name", "silver",
            "--processing_date_hour", PROCESSING_DATE_HOUR,
        ],
    )

    silver_anomaly_detection = SparkSubmitOperator(
        task_id="silver_batch_anomaly_detection",
        application=datagate_job_path("anomaly_detection"),
        conn_id="spark_default",
        deploy_mode="client",
        conf=DATAGATE_ANOMALY_SPARK_CONF,
        application_args=[
            "--datagate_db_conn_id", DATAGATE_DB_CONN_ID,
            "--connection_name", CONNECTION_NAME,
            "--schema_name", "silver",
            "--processing_date_hour", PROCESSING_DATE_HOUR,
            *DATAGATE_ANOMALY_JOB_ARGS,
        ],
    )

    gold_rule_verification = SparkSubmitOperator(
        task_id="gold_batch_rule_verification",
        application=datagate_job_path("rule_verification"),
        conn_id="spark_default",
        deploy_mode="client",
        conf=DATAGATE_SPARK_CONF,
        application_args=[
            "--datagate_db_conn_id", DATAGATE_DB_CONN_ID,
            "--connection_name", CONNECTION_NAME,
            "--schema_name", "gold",
            "--processing_date_hour", PROCESSING_DATE_HOUR,
        ],
    )

    rule_suggestion = SparkSubmitOperator(
        task_id="batch_rule_suggestion",
        application=datagate_job_path("rule_suggestion"),
        conn_id="spark_default",
        deploy_mode="client",
        conf=DATAGATE_SPARK_CONF,
        application_args=[
            "--datagate_db_conn_id", DATAGATE_DB_CONN_ID,
            "--connection_name", CONNECTION_NAME,
            "--schema_names", "silver", "gold",
            "--processing_date_hour", PROCESSING_DATE_HOUR,
        ],
    )

    ingest_data >> [bronze_meta, bronze_profile]
    bronze_meta >> bronze_meta_verify
    bronze_profile >> bronze_profile_verify
    [bronze_meta_verify, bronze_profile_verify] >> bronze_gate >> clean_data

    clean_data >> [silver_meta, silver_profile]
    silver_meta >> silver_meta_verify
    silver_profile >> silver_profile_verify
    [silver_meta_verify, silver_profile_verify] >> silver_rule_verification >> silver_anomaly_detection >> silver_gate >> transform_data

    transform_data >> [gold_meta, gold_profile]
    gold_meta >> gold_meta_verify
    gold_profile >> gold_profile_verify
    [gold_meta_verify, gold_profile_verify] >> gold_rule_verification >> gold_gate >> rule_suggestion
