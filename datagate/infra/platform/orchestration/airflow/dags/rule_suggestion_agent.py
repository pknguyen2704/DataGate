from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta


default_args = {
    "owner": "datagate",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


dag = DAG(
    "rule_suggestion_agent",
    default_args=default_args,
    description="Generate suggested data quality rules with PyDeequ on Spark",
    schedule_interval=None,
    catchup=False,
    tags=["datagate", "rules", "pydeequ"],
)


rule_suggestion_task = BashOperator(
    task_id="run_rule_suggestion",
    bash_command="""
        docker exec -e SPARK_VERSION=3.5 spark-master /opt/spark/bin/spark-submit \
            --master spark://spark-master:7077 \
            --deploy-mode client \
            --name rule-suggestion-{{ dag_run.run_id | replace(':', '-') | replace('+', '-') }} \
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
            /opt/spark/work-dir/datagate/rule_suggestion.py \
            --catalog {{ dag_run.conf.get('catalog', 'iceberg') }} \
            --schema {{ dag_run.conf.get('schema', 'public') }} \
            --table {{ dag_run.conf.get('table', 'unknown') }} \
            --sample_size {{ dag_run.conf.get('sample_size', 10000) }} \
            --backend_url http://host.docker.internal:8000
    """,
    dag=dag,
)


rule_suggestion_task
