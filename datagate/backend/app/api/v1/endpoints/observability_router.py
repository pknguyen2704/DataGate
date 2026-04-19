from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app import models, schemas
from app.api import deps
from app.services.observability_scheduler_service import trigger_airflow_dag
from app.api.v1.endpoints.services_router import (
    get_service_by_table_or_403,
    _get_owned_service,
    _get_accessible_services_query
)
from app.services.connection_manager_service import (
    get_tables as db_get_tables,
    get_sample_data as db_get_sample_data,
    get_table_metadata as db_get_table_metadata,
)
from app.services.observability_scanner_service import ObservabilityScanner
from app.services.observability_analyzer_service import run_metric_prediction

router = APIRouter()

@router.get("/metrics")
def get_metrics(
    table: str = Query(...),
    schema: Optional[str] = Query(None),
    column: Optional[str] = Query(None),
    db: Session = Depends(deps.get_db)
):
    """
    Lấy danh sách các chỉ số chất lượng dữ liệu (Deequ) của một bảng.
    Có thể lọc theo cột cụ thể.
    """
    full_table_name = f"{schema}.{table}" if schema else table
    query = db.query(models.DGObservabilityMetric).filter(
        models.DGObservabilityMetric.table_name == full_table_name
    )
    if column:
        query = query.filter(models.DGObservabilityMetric.column_name == column)
    
    return query.order_by(models.DGObservabilityMetric.snapshot_time.desc()).limit(200).all()

@router.get("/metric-predictions")
def get_metric_predictions(
    table: str = Query(...),
    metric: str = Query(...),
    schema: Optional[str] = Query(None),
    column: str = Query("*"),
    db: Session = Depends(deps.get_db)
):
    """
    Sử dụng Prophet để dự báo dải giá trị kỳ vọng cho một chỉ số cụ thể.
    """
    full_table_name = f"{schema}.{table}" if schema else table
    return run_metric_prediction(db, full_table_name, column, metric)

# --- 1. QUẢN LÝ LỊCH CHẠY (JOBS) ---

@router.get("/jobs", response_model=List[schemas.DGObservabilityConfig])
def list_jobs(db: Session = Depends(deps.get_db)):
    """
    Lấy danh sách cấu hình theo dõi của các bảng (dg_observability_config).
    Cấu hình này quyết định Airflow DAG sẽ quét những bảng nào hàng giờ.
    """
    return db.query(models.DGObservabilityConfig).all()

@router.get("/config", response_model=schemas.DGObservabilityConfig)
def get_config(
    table: str = Query(...),
    schema: str = Query(default="public"),
    catalog: str = Query(default="iceberg"),
    db: Session = Depends(deps.get_db)
):
    """
    Lấy cấu hình theo dõi của một bảng cụ thể. Nếu chưa có thì trả về object mặc định (chưa lưu).
    """
    config = db.query(models.DGObservabilityConfig).filter(
        models.DGObservabilityConfig.table_name == table,
        models.DGObservabilityConfig.schema_name == schema,
        models.DGObservabilityConfig.catalog == catalog
    ).first()

    if not config:
        # Trả về default để UI có thể hiển thị state
        return models.DGObservabilityConfig(
            id=0,
            table_name=table,
            schema_name=schema,
            catalog=catalog,
            is_active=False
        )
    return config

@router.put("/config", response_model=schemas.DGObservabilityConfig)
def update_config(
    payload: schemas.DGObservabilityConfigCreate,
    db: Session = Depends(deps.get_db)
):
    """
    Bật/tắt tính năng theo dõi hàng giờ cho một bảng.
    """
    config = db.query(models.DGObservabilityConfig).filter(
        models.DGObservabilityConfig.table_name == payload.table_name,
        models.DGObservabilityConfig.schema_name == payload.schema_name,
        models.DGObservabilityConfig.catalog == payload.catalog
    ).first()

    if not config:
        # Nếu chưa có thì tạo mới
        config = models.DGObservabilityConfig(
            table_name=payload.table_name,
            schema_name=payload.schema_name,
            catalog=payload.catalog,
            is_active=payload.is_active
        )
        db.add(config)
    else:
        config.is_active = payload.is_active

    db.commit()
    db.refresh(config)
    return config

@router.post("/trigger-scan")
def trigger_scan(
    payload: schemas.DGObservabilityTriggerOnDemand,
    db: Session = Depends(deps.get_db)
):
    """
    Kích hoạt quét (scan) metadata ngay lập tức cho một bảng bằng cách gọi Airflow DAG chạy thủ công.
    Phục vụ cho tính năng "Quét ngay" trên giao diện người dùng.
    """
    airflow_response = trigger_airflow_dag(
        "dg_observability_pipeline",
        {
            "job_type": "metadata_profile",
            "trigger_type": "manual",
            "catalog": payload.catalog,
            "schema": payload.schema_name,
            "table": payload.table_name,
        },
    )
    if "error" in airflow_response:
        raise HTTPException(status_code=502, detail=airflow_response["error"])
    return {"status": "success", "message": f"Đã bắt đầu quét bảng {payload.table_name}"}


# --- 2. DỮ LIỆU GIÁM SÁT (PILLAR 1 & 2) ---

@router.get("/snapshots", response_model=List[schemas.DGObservabilitySnapshot])
def get_snapshots(
    table: str = Query(...),
    schema: Optional[str] = Query(default=None),
    db: Session = Depends(deps.get_db)
):
    """
    Lấy thông tin tổng quan mới nhất của một bảng (Freshness và Volume).
    Freshness: Lần cập nhật cuối (dựa trên committed_at).
    Volume: Kích thước bảng và số lượng dòng hiện tại.
    """
    full_table_name = f"{schema}.{table}" if schema else table
    return db.query(models.DGObservabilitySnapshot).filter(
        models.DGObservabilitySnapshot.table_name == full_table_name
    ).order_by(models.DGObservabilitySnapshot.snapshot_time.desc()).limit(50).all()

@router.get("/volume-ts", response_model=List[schemas.DGObservabilityVolumeTS])
def get_volume_ts(
    table: str = Query(...),
    schema: Optional[str] = Query(default=None),
    db: Session = Depends(deps.get_db)
):
    """
    Lấy chuỗi thời gian tăng trưởng dữ liệu của bảng theo từng ngày.
    Dữ liệu này được biểu diễn trên biểu đồ và đưa vào Prophet dự báo Volume.
    """
    full_table_name = f"{schema}.{table}" if schema else table
    return db.query(models.DGObservabilityVolumeTS).filter(
        models.DGObservabilityVolumeTS.table_name == full_table_name
    ).order_by(models.DGObservabilityVolumeTS.dt.asc()).all()

@router.get("/schema", response_model=List[schemas.DGObservabilitySchema])
def get_schema(
    table: str = Query(...),
    schema: Optional[str] = Query(default=None),
    db: Session = Depends(deps.get_db)
):
    """
    Lấy danh sách các cột và kiểu dữ liệu hiện tại của bảng.
    Mục đích để phát hiện Schema Drift (thay đổi cấu trúc bất thường).
    """
    full_table_name = f"{schema}.{table}" if schema else table
    # Lấy thời điểm quét gần nhất
    latest = db.query(models.DGObservabilitySchema.snapshot_time).filter(
        models.DGObservabilitySchema.table_name == full_table_name
    ).order_by(models.DGObservabilitySchema.snapshot_time.desc()).first()
    
    if not latest: return []
    
    return db.query(models.DGObservabilitySchema).filter(
        models.DGObservabilitySchema.table_name == full_table_name,
        models.DGObservabilitySchema.snapshot_time == latest[0]
    ).all()


@router.get("/incidents", response_model=List[schemas.DGObservabilityIncident])
def get_incidents(
    table: Optional[str] = Query(default=None),
    schema: Optional[str] = Query(default=None),
    db: Session = Depends(deps.get_db)
):
    """
    Truy vấn bảng Incident để lấy tất cả những sự cố (bất thường) do Prophet 
    hoặc logic Schema Drift phát hiện ra đối với bảng đang xem.
    """
    query = db.query(models.DGObservabilityIncident)
    if table:
        full_table_name = f"{schema}.{table}" if schema else table
        query = query.filter(models.DGObservabilityIncident.table_name == full_table_name)
    return query.order_by(models.DGObservabilityIncident.detected_at.desc()).all()


# Monitoring data endpoints below

@router.post("/services/{service_id}/scan")
def scan_service(
    service_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Quét metadata của service (Pillar 1)."""
    _get_owned_service(db, service_id, current_user)
    return ObservabilityScanner.scan_service(db, service_id)

@router.post("/services/{service_id}/refresh-tables")
def refresh_service_tables(
    service_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Cập nhật danh sách bảng integrated từ DB thực tế."""
    service = _get_owned_service(db, service_id, current_user)
    try:
        real_tables = db_get_tables(service.connection_url)
        if service.integrated_tables:
            valid = [t for t in service.integrated_tables if t in real_tables]
            service.integrated_tables = valid
            db.add(service)
            db.commit()
            return {"status": "success", "updated_tables": valid}
        return {"status": "success", "message": "Không có bảng tích hợp để cập nhật"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- 3. PREDICTION DATA (cho Frontend charts) ---

@router.get("/volume-prediction")
def get_volume_prediction(
    table: str = Query(...),
    schema: Optional[str] = Query(default=None),
    db: Session = Depends(deps.get_db),
):
    """
    Cung cấp cả dữ liệu quá khứ và dự đoán tương lai (Prophet) về mức độ tăng trưởng (Volume).
    Dải trên (upper) và dưới (lower) được dùng vẽ dải kỳ vọng trên biểu đồ.
    """
    full_table_name = f"{schema}.{table}" if schema else table
    from app.services.observability_analyzer_service import ObservabilityAnalyzer
    return ObservabilityAnalyzer.get_volume_prediction(db, full_table_name)


@router.get("/freshness-prediction")
def get_freshness_prediction(
    table: str = Query(...),
    schema: Optional[str] = Query(default=None),
    db: Session = Depends(deps.get_db),
):
    """
    Dự báo thời gian chậm trễ tối đa cho bản cập nhật dữ liệu tiếp theo.
    Dải upper chính là "giới hạn trễ cho phép" tính bằng giờ.
    """
    full_table_name = f"{schema}.{table}" if schema else table
    from app.services.observability_analyzer_service import ObservabilityAnalyzer
    return ObservabilityAnalyzer.get_freshness_prediction(db, full_table_name)


# --- 4. INCIDENT MANAGEMENT ---

@router.put("/incidents/{incident_id}/resolve")
def resolve_incident(
    incident_id: int,
    db: Session = Depends(deps.get_db),
):
    """Đóng (resolve) một cảnh báo"""
    incident = db.query(models.DGObservabilityIncident).filter(models.DGObservabilityIncident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    incident.status = "resolved"
    db.commit()
    return {"status": "success", "message": f"Incident {incident_id} resolved"}


# --- 5. SCHEMA CHANGE HISTORY ---

@router.get("/schema-history")
def get_schema_history(
    table: str = Query(...),
    schema: Optional[str] = Query(default=None),
    db: Session = Depends(deps.get_db),
):
    """
    Trả về lịch sử thay đổi cấu trúc bảng (Schema).
    Hàm này so sánh tuần tự giữa các thời điểm (snapshot_time) liền kề 
    để tìm ra những cột được thêm, xóa hoặc đổi kiểu.
    """
    full_table_name = f"{schema}.{table}" if schema else table

    # Lấy tất cả các thời điểm quét schema
    snapshot_times = db.query(models.DGObservabilitySchema.snapshot_time)\
        .filter(models.DGObservabilitySchema.table_name == full_table_name)\
        .distinct().order_by(models.DGObservabilitySchema.snapshot_time.desc()).limit(20).all()

    changes = []
    for i in range(len(snapshot_times) - 1):
        current_time = snapshot_times[i][0]
        prev_time = snapshot_times[i + 1][0]

        current_schema = db.query(models.DGObservabilitySchema).filter(
            models.DGObservabilitySchema.table_name == full_table_name,
            models.DGObservabilitySchema.snapshot_time == current_time
        ).all()
        prev_schema = db.query(models.DGObservabilitySchema).filter(
            models.DGObservabilitySchema.table_name == full_table_name,
            models.DGObservabilitySchema.snapshot_time == prev_time
        ).all()

        current_cols = {c.column_name: c.data_type for c in current_schema}
        prev_cols = {c.column_name: c.data_type for c in prev_schema}

        diffs = []
        for col, dtype in prev_cols.items():
            if col not in current_cols:
                diffs.append({"column": col, "change": "removed", "old_type": dtype, "new_type": None})
            elif dtype != current_cols[col]:
                diffs.append({"column": col, "change": "type_changed", "old_type": dtype, "new_type": current_cols[col]})

        for col in current_cols:
            if col not in prev_cols:
                diffs.append({"column": col, "change": "added", "old_type": None, "new_type": current_cols[col]})

        if diffs:
            changes.append({
                "snapshot_time": str(current_time),
                "compared_to": str(prev_time),
                "changes": diffs,
            })

    return {
        "table_name": full_table_name,
        "total_snapshots": len(snapshot_times),
        "changes": changes,
    }

