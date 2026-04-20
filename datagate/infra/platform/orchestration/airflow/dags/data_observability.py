import logging
import pandas as pd
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.trino.hooks.trino import TrinoHook
from prophet import Prophet

# Khởi tạo logger để ghi lại các log trong quá trình chạy DAG
logger = logging.getLogger(__name__)

# Cấu hình mặc định cho DAG: chủ sở hữu, số lần thử lại, thời gian chờ giữa các lần thử
default_args = {
    "owner": "datagate",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

def get_active_tables():
    """
    BƯỚC 0: Xác định mục tiêu giám sát.
    Truy vấn bảng 'integrated_tables' (Danh sách các bảng đã đăng ký từ Trino)
    để lấy danh sách các bảng đang ở trạng thái active.
    """
    pg_hook = PostgresHook(postgres_conn_id="datagate_db_default")
    sql = "SELECT catalog, schema_name, table_name FROM integrated_tables WHERE is_active = TRUE"
    rows = pg_hook.get_records(sql)
    
    active_list = [{"catalog": r[0], "schema": r[1], "table": r[2]} for r in rows]
    logger.info(f"Found {len(active_list)} active tables for observability: {active_list}")
    return active_list

def collect_metadata_task(**kwargs):
    """
    BƯỚC 1: Thu thập Metadata từ Trino.
    Kết nối tới Trino (Engine chính) để lấy các thông số kỹ thuật của từng bảng:
    - Snapshots: Để biết thời điểm cập nhật cuối và kích thước dữ liệu (chỉ áp dụng cho Iceberg).
    - Row Count: Tổng số bản ghi hiện tại.
    - Information Schema: Cấu trúc các cột và kiểu dữ liệu hiện tại.
    """
    trino_hook = TrinoHook(trino_conn_id="trino_default")
    tables = get_active_tables()
    metadatas = []

    for t in tables:
        catalog, schema, table = t['catalog'], t['schema'], t['table']
        try:
            # 1.1 Lấy thông tin Snapshot (Freshness & Size) từ bảng Iceberg metadata
            snap_sql = f"""
                SELECT 
                    committed_at, 
                    summary['added-records'],
                    summary['total-data-files-size']
                FROM {catalog}.{schema}."{table}$snapshots" 
                ORDER BY committed_at DESC LIMIT 1
            """
            snap = trino_hook.get_first(snap_sql)
            
            # 1.2 Đếm tổng số dòng (Volume)
            count_sql = f"SELECT count(*) FROM {catalog}.{schema}.{table}"
            count = trino_hook.get_first(count_sql)
            
            # 1.3 Lấy thông tin cấu trúc cột (Schema)
            cols_sql = f"""
                SELECT column_name, data_type 
                FROM {catalog}.information_schema.columns 
                WHERE table_schema = '{schema}' AND table_name = '{table}'
            """
            cols = trino_hook.get_records(cols_sql)

            # Đóng gói dữ liệu để chuyển sang task tiếp theo qua XCom
            metadatas.append({
                "catalog": catalog,
                "schema": schema,
                "table": table,
                "last_updated": snap[0].isoformat() if snap and snap[0] else None,
                "added_records": int(snap[1]) if snap and snap[1] else 0,
                "total_size": int(snap[2]) if snap and snap[2] else 0,
                "total_records": count[0] if count else 0,
                "columns": [{"name": c[0], "type": c[1]} for c in cols],
                "snapshot_time": datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Error collecting metadata for {table}: {e}")

    return metadatas

def save_and_analyze_metadata_task(**kwargs):
    """
    BƯỚC 2: Lưu trữ và Phân tích Schema Drift.
    - So sánh schema hiện tại vừa lấy được với schema được lưu ở lần chạy trước.
    - Nếu có sự thay đổi (Thêm/Xóa cột, đổi kiểu dữ liệu) -> Tạo một Incident (Schema Drift).
    - Lưu các thông số Snapshot và Volume vào database để phục vụ vẽ biểu đồ.
    """
    ti = kwargs['ti']
    metadatas = ti.xcom_pull(task_ids='collect_metadata')
    if not metadatas:
        return

    pg_hook = PostgresHook(postgres_conn_id="datagate_db_default")
    for m in metadatas:
        catalog, schema, table = m['catalog'], m['schema'], m['table']
        now = m['snapshot_time']

        # 2.1 KIỂM TRA SCHEMA DRIFT
        # Lấy schema cũ nhất từ DB
        prev_cols_sql = f"""
            SELECT column_name, data_type FROM observability_schema 
            WHERE table_name='{table}' AND schema_name='{schema}' 
            AND snapshot_time = (SELECT MAX(snapshot_time) FROM observability_schema WHERE table_name='{table}' AND schema_name='{schema}')
        """
        prev_cols_raw = pg_hook.get_records(prev_cols_sql)
        if prev_cols_raw:
            prev_cols = {r[0]: r[1] for r in prev_cols_raw}
            current_cols = {c['name']: c['type'] for c in m['columns']}
            
            drifts = []
            # Kiểm tra cột bị xóa hoặc đổi kiểu
            for col, dtype in prev_cols.items():
                if col not in current_cols:
                    drifts.append(f"Removed column '{col}'")
                elif dtype != current_cols[col]:
                    drifts.append(f"Changed type of '{col}': {dtype} -> {current_cols[col]}")
            # Kiểm tra cột mới được thêm
            for col in current_cols:
                if col not in prev_cols:
                    drifts.append(f"Added new column '{col}'")
            
            # Nếu phát hiện drift, ghi vào bảng cảnh báo (Incidents)
            if drifts:
                pg_hook.run(
                    "INSERT INTO observability_incidents (catalog, schema_name, table_name, incident_type, severity, message) VALUES (%s, %s, %s, %s, %s, %s)",
                    parameters=(catalog, schema, table, 'drift', 'medium', "; ".join(drifts))
                )

        # 2.2 LƯU DỮ LIỆU SNAPSHOT (Kích thước & Tổng số dòng)
        pg_hook.run(
            """INSERT INTO observability_snapshots 
               (catalog, schema_name, table_name, snapshot_time, last_updated_time, total_records, total_size) 
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            parameters=(catalog, schema, table, now, m['last_updated'], m['total_records'], m['total_size'])
        )
        
        # 2.3 LƯU DỮ LIỆU VOLUME (Số lượng bản ghi mới thêm vào tại thời điểm này)
        pg_hook.run(
            """INSERT INTO observability_volume_ts (catalog, schema_name, table_name, dt, records_added) 
               VALUES (%s, %s, %s, %s, %s)""",
            parameters=(catalog, schema, table, m['last_updated'] or now, m['added_records'])
        )
        
        # 2.4 CẬP NHẬT TRẠNG THÁI SCHEMA MỚI NHẤT
        for col in m['columns']:
            pg_hook.run(
                """INSERT INTO observability_schema (catalog, schema_name, table_name, column_name, data_type, snapshot_time) 
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                parameters=(catalog, schema, table, col['name'], col['type'], now)
            )

def run_prophet_task(**kwargs):
    """
    BƯỚC 3: Phát hiện bất thường về lưu lượng (Volume Anomaly) bằng AI (Prophet).
    - Lấy lịch sử số lượng bản ghi mới (Volume) trong quá khứ.
    - Sử dụng thư viện Prophet của Meta để huấn luyện mô hình dự báo.
    - Nếu số lượng bản ghi vừa thu thập nằm ngoài khoảng dự báo (yhat_lower, yhat_upper) 
      -> Ghi nhận một Incident (Volume Anomaly).
    """
    pg_hook = PostgresHook(postgres_conn_id="datagate_db_default")
    tables = get_active_tables()

    for t in tables:
        catalog, schema, table = t['catalog'], t['schema'], t['table']
        
        # 3.1 Lấy dữ liệu chuỗi thời gian (Time-series) cho bảng
        sql = f"""
            SELECT dt, records_added FROM observability_volume_ts 
            WHERE table_name='{table}' AND schema_name='{schema}' 
            ORDER BY dt ASC
        """
        history = pg_hook.get_records(sql)

        # Cần ít nhất 7 điểm dữ liệu để mô hình có thể dự báo cơ bản
        if len(history) < 7:
            logger.info(f"Not enough history for {table} to run Prophet analysis.")
            continue

        # 3.2 Chuẩn bị dữ liệu cho Prophet (ds: datestamp, y: value)
        df = pd.DataFrame(history, columns=['ds', 'y'])
        df['ds'] = pd.to_datetime(df['ds'])

        # 3.3 Huấn luyện mô hình với khoảng tin cậy 95%
        model = Prophet(interval_width=0.95, daily_seasonality=True, yearly_seasonality=False)
        model.fit(df)

        # 3.4 Dự báo cho thời điểm hiện tại và so sánh với thực tế
        forecast = model.predict(df.tail(1))
        res = forecast.iloc[0]
        actual = df.iloc[-1]['y']

        # Nếu giá trị thực tế nằm ngoài khoảng kỳ vọng của AI
        if actual < res['yhat_lower'] or actual > res['yhat_upper']:
            msg = f"Volume anomaly detected on {table}: Actual {actual}, Expected range [{res['yhat_lower']:.0f}, {res['yhat_upper']:.0f}]"
            pg_hook.run(
                "INSERT INTO observability_incidents (catalog, schema_name, table_name, incident_type, severity, message) VALUES (%s, %s, %s, %s, %s, %s)",
                parameters=(catalog, schema, table, 'volume', 'high', msg)
            )

# KHAI BÁO DAG
with DAG(
    dag_id="data_observability",
    default_args=default_args,
    description="Full Data Observability Analysis Pipeline",
    schedule_interval="@hourly", # Mặc định chạy cấu hình mỗi giờ một lần
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["datagate", "observability", "prophet", "iceberg"]
) as dag:

    # Task 1: Quét Metadata từ Trino
    collect_metadata = PythonOperator(
        task_id="collect_metadata",
        python_callable=collect_metadata_task,
    )

    # Task 2: Lưu vào DB và check biến động cấu trúc (Schema Drift)
    save_and_analyze = PythonOperator(
        task_id="save_and_analyze",
        python_callable=save_and_analyze_metadata_task,
    )

    # Task 3: Chạy mô hình AI phát hiện bất thường về số lượng dòng
    run_prophet = PythonOperator(
        task_id="run_prophet",
        python_callable=run_prophet_task,
    )

    # Xác định thứ tự thực hiện của các Task
    collect_metadata >> save_and_analyze >> run_prophet
