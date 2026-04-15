from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import json

default_args = {
    'owner': 'datagate',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'ml_anomaly_agent',
    default_args=default_args,
    description='ML Anomaly Detection Agent using XGBoost & SHAP on Spark',
    schedule_interval=None, # Triggered via API
    catchup=False,
    tags=['datagate', 'ml', 'anomaly'],
)

# This task runs spark-submit directly on the spark-master container.
# Spark standalone does not support cluster deploy mode for Python applications,
# so this stays in client mode.
# It receives parameters from the external trigger (dag_run.conf).
ml_scan_task = BashOperator(
    task_id='run_ml_anomaly_scan',
    bash_command="""
        docker exec spark-master /opt/spark/bin/spark-submit \
            --master spark://spark-master:7077 \
            --deploy-mode client \
            --name ml-anomaly-{{ dag_run.run_id | replace(':', '-') | replace('+', '-') }} \
            --conf spark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions \
            --conf spark.sql.catalog.iceberg=org.apache.iceberg.spark.SparkCatalog \
            --conf spark.sql.catalog.iceberg.catalog-impl=org.apache.iceberg.rest.RESTCatalog \
            --conf spark.sql.catalog.iceberg.uri=http://iceberg-rest:8181 \
            --conf spark.sql.catalog.iceberg.s3.endpoint=http://minio:9000 \
            --conf spark.sql.catalog.iceberg.s3.access-key-id=admin \
            --conf spark.sql.catalog.iceberg.s3.secret-access-key=miniopassword \
            --conf spark.sql.catalog.iceberg.s3.path-style-access=true \
            --conf spark.sql.catalog.iceberg.s3.region=us-east-1 \
            --conf spark.hadoop.fs.s3a.impl=org.apache.hadoop.fs.s3a.S3AFileSystem \
            --conf spark.hadoop.fs.s3a.endpoint=http://minio:9000 \
            --conf spark.hadoop.fs.s3a.access.key=admin \
            --conf spark.hadoop.fs.s3a.secret.key=miniopassword \
            --conf spark.hadoop.fs.s3a.path.style.access=true \
            /opt/spark/work-dir/datagate/ml_anomaly_detection.py \
            --catalog {{ dag_run.conf.get('catalog', 'iceberg') }} \
            --schema {{ dag_run.conf.get('schema', 'public') }} \
            --table {{ dag_run.conf.get('table', 'unknown') }} \
            --effective_date {{ dag_run.conf.get('effective_date', '') }} \
            --sample_size {{ dag_run.conf.get('sample_size', 10000) }} \
            --sensitivity {{ dag_run.conf.get('sensitivity', 'medium') }} \
            --backend_url http://host.docker.internal:8000 \
            --token internal_ops_token
    """,
    dag=dag,
)

ml_scan_task
