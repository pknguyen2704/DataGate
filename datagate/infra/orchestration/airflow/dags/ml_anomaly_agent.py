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

# This task will run spark-submit inside the spark-client container
# It receives parameters from the external trigger (dag_run.conf)
# Required conf keys: catalog, schema, table
ml_scan_task = BashOperator(
    task_id='run_ml_anomaly_scan',
    bash_command="""
        docker exec spark-client /opt/spark/bin/spark-submit \
            --master spark://spark-master:7077 \
            --deploy-mode client \
            --conf spark.sql.catalog.iceberg=org.apache.iceberg.spark.SparkCatalog \
            --conf spark.sql.catalog.iceberg.type=hadoop \
            --conf spark.sql.catalog.iceberg.warehouse=s3a://iceberg/warehouse \
            --conf spark.sql.catalog.iceberg.io-impl=org.apache.iceberg.aws.s3.S3FileIO \
            --conf spark.hadoop.fs.s3a.endpoint=http://minio:9000 \
            --conf spark.hadoop.fs.s3a.access.key=admin \
            --conf spark.hadoop.fs.s3a.secret.key=miniopassword \
            --conf spark.hadoop.fs.s3a.path.style.access=true \
            /opt/spark/work-dir/datagate/ml_anomaly_detection.py \
            --catalog {{ dag_run.conf.get('catalog', 'iceberg') }} \
            --schema {{ dag_run.conf.get('schema', 'public') }} \
            --table {{ dag_run.conf.get('table', 'unknown') }} \
            --backend_url http://backend:8000 \
            --token internal_ops_token
    """,
    dag=dag,
)

ml_scan_task
