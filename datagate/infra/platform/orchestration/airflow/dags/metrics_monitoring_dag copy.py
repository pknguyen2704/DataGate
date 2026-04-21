from datetime import datetime, timedelta
import logging
import json

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.utils.task_group import TaskGroup

logger = logging.getLogger(__name__)

default_args = {
    "owner": "datagate",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

def fetch_active_configs():
    """
    Lấy danh sách các bảng đang bật tính năng theo dõi.
    """
    pg_hook = PostgresHook(postgres_conn_id="datagate_db_default")
    records = pg_hook.get_records(
        "SELECT id, catalog, schema_name, table_name FROM dg_observability_config WHERE is_active = TRUE"
    )
    return [
        {"id": r[0], "catalog": r[1], "schema": r[2], "table": r[3]}
        for r in records
    ]

def run_metric_anomaly_detection_task(full_table_name, **kwargs):
    """
    Sau khi Spark job hoàn thành, chạy Prophet để phân tích các metrics vừa thu thập.
    """
    pg_hook = PostgresHook(postgres_conn_id="datagate_db_default")
    # TODO: Thực hiện gọi hàm phân tích chuỗi thời gian cho các metrics của bảng này
    # Logic tương tự như Volume Anomaly nhưng lặp qua từng (column_name, metric_name)
    logger.info(f"Running metric anomaly detection for {full_table_name}")
    pass

with DAG(
    dag_id="dg_metrics_monitoring_pipeline",
    default_args=default_args,
    description="Giám sát chất lượng dữ liệu cấp độ cột sử dụng PyDeequ và Prophet",
    schedule_interval="@daily", # Quét sâu nên chạy hàng ngày hoặc 6 tiếng một lần
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=["datagate", "quality", "deequ"],
) as dag:

    # 1. Lấy danh sách targets
    fetch_targets = PythonOperator(
        task_id="fetch_targets",
        python_callable=fetch_active_configs,
    )

    # 2. Với mỗi target, chạy Spark Deequ Job và sau đó chạy Anomaly Detection
    # Sử dụng Dynamic Task Mapping hoặc TaskGroup (ở đây dùng Python loop tạo task đơn giản cho demo)
    # Trong môi trường thực tế nên dùng Expand của Airflow 2.3+
    
    # Tuy nhiên, do fetch_targets chạy ở runtime, ta cần một cách để tạo task động.
    # Một cách phổ biến là dùng PythonOperator để trigger các sub-dags hoặc dùng Dynamic Task Mapping.
    # Ở đây tôi sẽ viết một hàm Python để tạo các SparkSubmitOperator tasks dựa trên kết quả của fetch_targets
    
    def generate_spark_tasks(**kwargs):
        ti = kwargs['ti']
        configs = ti.xcom_pull(task_ids='fetch_targets')
        run_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for config in configs:
            catalog = config['catalog']
            schema = config['schema']
            table = config['table']
            full_table_name = f"{schema}.{table}"
            
            # Trigger Spark Submit
            # Chú ý: Trong Airflow thực tế, ta không thể tạo task bên trong PythonOperator như thế này.
            # Ta nên dùng `expand` hoặc cấu hình DAG để parse lại.
            # Để đơn giản và đúng chuẩn Airflow 2.x, tôi sẽ dùng cấu trúc DAG linh hoạt.
            pass

    # Để đảm bảo code chạy được ngay, tôi sẽ viết theo kiểu "Loop over fixed list" nếu fetch_targets không đổi
    # Hoặc tốt hơn, dùng một Task duy nhất chạy loop Spark Submit (không khuyến khích)
    # Lựa chọn tốt nhất: Viết DAG có khả năng tự cấu hình.
    
    # Giả sử ta lấy targets ở thời điểm parse DAG (nếu DB ổn định)
    try:
        pg_hook = PostgresHook(postgres_conn_id="datagate_db_default")
        configs = pg_hook.get_records(
            "SELECT catalog, schema_name, table_name FROM dg_observability_config WHERE is_active = TRUE"
        )
    except:
        configs = []

    for catalog, schema, table in configs:
        full_table_name = f"{schema}.{table}"
        safe_name = full_table_name.replace(".", "_")
        
        with TaskGroup(group_id=f"monitor_{safe_name}") as tg:
            spark_analyze = SparkSubmitOperator(
                task_id="pyspark_deequ_analysis",
                application="/opt/spark/jobs/datagate/datagate_deequ_analysis.py",
                conn_id="spark_default",
                java_class=None,
                packages="com.amazon.deequ:deequ:2.0.3-spark-3.3", # Cần package deequ
                application_args=[
                    catalog,
                    schema,
                    table,
                    "{{ ts }}"
                ],
                conf={
                    "spark.serializer": "org.apache.spark.serializer.KryoSerializer",
                    "spark.sql.extensions": "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
                },
                env_vars={
                    "POSTGRES_HOST": "postgres",
                    "POSTGRES_DB": "datagate",
                    "POSTGRES_USER": "admin",
                    "POSTGRES_PASSWORD": "datagatepassword"
                }
            )
            
            anomaly_detect = PythonOperator(
                task_id="metric_anomaly_detection",
                python_callable=run_metric_anomaly_detection_task,
                op_kwargs={"full_table_name": full_table_name},
            )
            
            spark_analyze >> anomaly_detect
            
            fetch_targets >> tg
