from datetime import datetime, timedelta
import logging

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.trino.hooks.trino import TrinoHook

logger = logging.getLogger(__name__)

default_args = {
    "owner": "datagate",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

def fetch_active_configs(pg_hook):
    """
    Truy vấn bảng dg_observability_config để lấy danh sách các bảng đang bật tính năng theo dõi (is_active = TRUE).
    Airflow sẽ chỉ quét các bảng có bật cờ này để tiết kiệm tài nguyên.
    """
    records = pg_hook.get_records(
        "SELECT id, catalog, schema_name, table_name FROM dg_observability_config WHERE is_active = TRUE"
    )
    return [
        {"id": r[0], "catalog": r[1], "schema": r[2], "table": r[3]}
        for r in records
    ]

def collect_table_metadata(trino_hook, catalog, schema, table):
    """
    Thu thập các thông tin metadata cần thiết từ hệ thống (Iceberg/Trino) mà KHÔNG cần quét dữ liệu thực:
    - freshness: Lấy thời điểm commit cuối cùng.
    - volume: Lấy số lượng bản ghi và dung lượng byte từ bảng metadata files.
    - volume_ts: Lấy lịch sử nạp dữ liệu theo từng ngày để đưa vào mô hình Prophet phân tích xu hướng.
    - schema: Lấy danh sách cột và kiểu dữ liệu để phát hiện xem cấu trúc có bị thay đổi (schema drift) không.
    """
    queries = {
        "freshness": f'SELECT MAX(committed_at) FROM {catalog}.{schema}."{table}$snapshots"',
        "volume": f'SELECT SUM(record_count), SUM(file_size_in_bytes) FROM {catalog}.{schema}."{table}$files"',
        "volume_ts": f"""
            SELECT date_trunc('day', committed_at) AS dt,
                   SUM(CAST(element_at(summary, 'added-records') AS BIGINT))
            FROM {catalog}.{schema}."{table}$snapshots"
            GROUP BY 1
        """,
        "schema": f"""
            SELECT column_name, data_type
            FROM {catalog}.information_schema.columns
            WHERE table_schema = '{schema}' AND table_name = '{table}'
        """,
    }

    results = {}
    for key, query in queries.items():
        try:
            res = trino_hook.get_records(query)
            results[key] = res
        except Exception as e:
            logger.warning(f"Failed to execute query for {key} on {catalog}.{schema}.{table}: {e}")
            results[key] = []
    return results

def persist_metadata(pg_hook, full_table_name, results, run_ts):
    """
    Lưu các metadata thu thập được từ Trino vào PostgreSQL (các bảng dg_observability_*) 
    để frontend có thể hiển thị biểu đồ và để Analyzer tính toán bất thường.
    """
    # 1. Lưu thông tin snapshot hiện tại (Freshness & Volume tĩnh)
    # DGObservabilitySnapshot
    volume_rows = results.get("volume", [])
    freshness_rows = results.get("freshness", [])
    if volume_rows and volume_rows[0][0] is not None:
        pg_hook.run(
            """
            INSERT INTO dg_observability_snapshots (table_name, snapshot_time, last_updated_time, total_records, total_size)
            VALUES (%s, %s, %s, %s, %s)
            """,
            parameters=(
                full_table_name,
                run_ts,
                freshness_rows[0][0] if freshness_rows else None,
                volume_rows[0][0],
                volume_rows[0][1],
            ),
            autocommit=True,
        )

    # 2. Lưu lại lịch sử gia tăng dữ liệu từng ngày (để dùng cho Prophet Volume Prediction)
    # DGObservabilityVolumeTS
    for row in results.get("volume_ts", []):
        if row[0] is None:
            continue
        pg_hook.run("DELETE FROM dg_observability_volume_ts WHERE table_name = %s AND dt = %s", parameters=(full_table_name, row[0]), autocommit=True)
        pg_hook.run(
            "INSERT INTO dg_observability_volume_ts (table_name, dt, records_added) VALUES (%s, %s, %s)",
            parameters=(full_table_name, row[0], row[1]),
            autocommit=True,
        )

    # 3. Lưu lại cấu trúc cột hiện tại để so sánh sự thay đổi (Schema Drift)
    # DGObservabilitySchema
    for row in results.get("schema", []):
        pg_hook.run(
            "INSERT INTO dg_observability_schema (table_name, column_name, data_type, snapshot_time) VALUES (%s, %s, %s, %s)",
            parameters=(full_table_name, row[0], row[1], run_ts),
            autocommit=True,
        )

def run_anomaly_detection(pg_hook, full_table_name):
    """
    Khởi chạy quá trình phân tích (Analyzer).
    Bước này sẽ gọi đến ObservabilityAnalyzer (nơi chạy mô hình Prophet) để đánh giá xem 
    những dữ liệu metadata vừa thu thập có chứa bất thường nào không (đến muộn, dữ liệu ít bất thường...).
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    conn_uri = pg_hook.get_uri()
    engine = create_engine(conn_uri)
    Session = sessionmaker(bind=engine)
    db = Session()

    try:
        from app.services.observability_analyzer_service import ObservabilityAnalyzer
        ObservabilityAnalyzer.analyze_table(db, full_table_name)
    except Exception as e:
        logger.warning(f"Analyzer failed or not available for {full_table_name}: {e}")
    finally:
        db.close()

def log_run_start(pg_hook, config_id, dag_id, dag_run_id, scheduled_for):
    if not config_id:
        return None
    records = pg_hook.get_records(
        """
        INSERT INTO dg_observability_run_history (job_id, dag_id, dag_run_id, trigger_type, status, started_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        parameters=(config_id, dag_id, dag_run_id, "manual" if "manual" in dag_run_id else "scheduled", "running", scheduled_for),
    )
    return records[0][0] if records else None

def log_run_finish(pg_hook, history_id, status, error_message=None):
    if not history_id:
        return
    pg_hook.run(
        """
        UPDATE dg_observability_run_history
        SET status = %s, finished_at = %s, error_message = %s
        WHERE id = %s
        """,
        parameters=(status, datetime.utcnow(), error_message, history_id),
        autocommit=True,
    )

def fetch_targets(**kwargs):
    """
    Bước 1: Xác định danh sách các bảng cần quét.
    Nếu chạy thủ công (qua UI), lấy thông tin bảng từ dag_run.conf.
    Nếu chạy tự động (hàng giờ), lấy tất cả các bảng có is_active = TRUE.
    """
    dag_run = kwargs.get("dag_run")
    pg_hook = PostgresHook(postgres_conn_id="datagate_db_default")
    
    # Kiểm tra xem có phải chạy thủ công 1 bảng không
    if dag_run and dag_run.conf and dag_run.conf.get("table"):
        catalog = dag_run.conf.get("catalog", "iceberg")
        schema = dag_run.conf.get("schema", "public")
        table = dag_run.conf.get("table")
        
        # Tìm ID của config nếu có
        records = pg_hook.get_records(
            "SELECT id FROM dg_observability_config WHERE catalog=%s AND schema_name=%s AND table_name=%s",
            parameters=(catalog, schema, table)
        )
        config_id = records[0][0] if records else None
        
        return [{"id": config_id, "catalog": catalog, "schema": schema, "table": table}]

    # Nếu không, lấy các bảng đang được bật
    return fetch_active_configs(pg_hook)

def collect_and_persist_task(**kwargs):
    """
    Bước 2: Thu thập metadata từ Trino và lưu vào CSDL.
    """
    ti = kwargs["ti"]
    configs = ti.xcom_pull(task_ids="fetch_targets")
    if not configs:
        logger.info("No targets to process.")
        return

    pg_hook = PostgresHook(postgres_conn_id="datagate_db_default")
    trino_hook = TrinoHook(trino_conn_id="trino_default")
    
    dag_id = kwargs["dag"].dag_id
    dag_run_id = kwargs["run_id"]
    run_ts = datetime.utcnow()

    # Dùng XCom để truyền history_ids sang task sau
    history_ids = {}

    for config in configs:
        catalog = config.get("catalog") or "iceberg"
        schema = config.get("schema") or "public"
        table = config.get("table")
        config_id = config.get("id")
        
        # Đồng nhất định dạng table_name trong DB là 'schema.table' (bỏ catalog) để khớp với Backend Router
        full_table_name = f"{schema}.{table}" if schema else table
        
        history_id = log_run_start(pg_hook, config_id, dag_id, dag_run_id, run_ts)
        history_ids[full_table_name] = history_id
        
        try:
            results = collect_table_metadata(trino_hook, catalog, schema, table)
            persist_metadata(pg_hook, full_table_name, results, run_ts)
            
            if config_id:
                pg_hook.run(
                    "UPDATE dg_observability_config SET last_run_at = %s WHERE id = %s",
                    parameters=(run_ts, config_id),
                    autocommit=True
                )
        except Exception as e:
            logger.error(f"Error collecting metadata for {full_table_name}: {e}")
            log_run_finish(pg_hook, history_id, "failed", str(e))
            history_ids[full_table_name] = None # Đánh dấu lỗi để task sau không chạy hoặc update status

    return history_ids

def run_anomaly_detection_task(**kwargs):
    """
    Bước 3: Chạy mô hình Prophet để tìm bất thường (Anomaly Detection).
    """
    ti = kwargs["ti"]
    configs = ti.xcom_pull(task_ids="fetch_targets")
    history_ids = ti.xcom_pull(task_ids="collect_and_persist")
    
    if not configs or not history_ids:
        return

    pg_hook = PostgresHook(postgres_conn_id="datagate_db_default")
    
    for config in configs:
        schema = config.get("schema") or "public"
        table = config.get("table")
        full_table_name = f"{schema}.{table}" if schema else table
        
        history_id = history_ids.get(full_table_name)
        if not history_id:
            continue # Đã lỗi ở bước trước, bỏ qua
            
        try:
            run_anomaly_detection(pg_hook, full_table_name)
            log_run_finish(pg_hook, history_id, "success")
        except Exception as e:
            logger.error(f"Error in anomaly detection for {full_table_name}: {e}")
            log_run_finish(pg_hook, history_id, "failed", str(e))

with DAG(
    dag_id="dg_observability_pipeline",
    default_args=default_args,
    description="Chạy kiểm tra Data Observability định kỳ hàng giờ cho các bảng được cấu hình bật",
    schedule_interval="@hourly", # Chạy tự động mỗi giờ
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=["datagate", "observability"],
) as dag:

    t1_fetch = PythonOperator(
        task_id="fetch_targets",
        python_callable=fetch_targets,
        provide_context=True,
    )

    t2_collect = PythonOperator(
        task_id="collect_and_persist",
        python_callable=collect_and_persist_task,
        provide_context=True,
    )

    t3_analyze = PythonOperator(
        task_id="run_anomaly_detection",
        python_callable=run_anomaly_detection_task,
        provide_context=True,
    )

    # Định nghĩa luồng phụ thuộc của các task
    t1_fetch >> t2_collect >> t3_analyze
