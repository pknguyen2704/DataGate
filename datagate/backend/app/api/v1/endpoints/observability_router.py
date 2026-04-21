from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app import models, schemas
from app.api import deps
from app.services.observability_scheduler_service import trigger_airflow_dag

router = APIRouter()

# --- 1. CONFIGURATION ---

@router.get("/config", response_model=schemas.ObservabilityConfig)
def get_config(
    table: str = Query(...),
    schema: str = Query(default="public"),
    catalog: str = Query(default="iceberg"),
    db: Session = Depends(deps.get_db)
):
    """Lấy cấu hình theo dõi của một bảng."""
    config = db.query(models.ObservabilityConfig).filter(
        models.ObservabilityConfig.table_name == table,
        models.ObservabilityConfig.schema_name == schema,
        models.ObservabilityConfig.catalog == catalog
    ).first()

    if not config:
        return models.ObservabilityConfig(
            id=0, table_name=table, schema_name=schema, catalog=catalog, is_active=False
        )
    return config

@router.put("/config", response_model=schemas.ObservabilityConfig)
def update_config(
    payload: schemas.ObservabilityConfigCreate,
    db: Session = Depends(deps.get_db)
):
    """Bật/tắt theo dõi bảng."""
    config = db.query(models.ObservabilityConfig).filter(
        models.ObservabilityConfig.table_name == payload.table_name,
        models.ObservabilityConfig.schema_name == payload.schema_name,
        models.ObservabilityConfig.catalog == payload.catalog
    ).first()

    if not config:
        config = models.ObservabilityConfig(
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
    payload: schemas.ObservabilityTriggerOnDemand,
    db: Session = Depends(deps.get_db)
):
    """Kích hoạt Airflow DAG ngay lập tức."""
    airflow_response = trigger_airflow_dag(
        "data_observability",
        {
            "catalog": payload.catalog,
            "schema": payload.schema_name,
            "table": payload.table_name,
        },
    )
    if "error" in airflow_response:
        raise HTTPException(status_code=502, detail=airflow_response["error"])
    return {"status": "success", "message": f"Đã trigger scan cho bảng {payload.table_name}"}

# --- 2. METADATA & OBSERVABILITY DATA ---

@router.get("/snapshots", response_model=List[schemas.ObservabilitySnapshot])
def get_snapshots(
    table: str = Query(...),
    schema: str = Query(...),
    catalog: str = Query(default="iceberg"),
    db: Session = Depends(deps.get_db)
):
    """Lấy lịch sử Freshness & Volume (Row count, Size)."""
    return db.query(models.ObservabilitySnapshot).filter(
        models.ObservabilitySnapshot.table_name == table,
        models.ObservabilitySnapshot.schema_name == schema,
        models.ObservabilitySnapshot.catalog == catalog
    ).order_by(models.ObservabilitySnapshot.snapshot_time.desc()).limit(50).all()

@router.get("/schema", response_model=List[schemas.ObservabilitySchema])
def get_schema(
    table: str = Query(...),
    schema: str = Query(...),
    catalog: str = Query(default="iceberg"),
    db: Session = Depends(deps.get_db)
):
    """Lấy cấu trúc cột hiện tại."""
    latest = db.query(models.ObservabilitySchema.snapshot_time).filter(
        models.ObservabilitySchema.table_name == table,
        models.ObservabilitySchema.schema_name == schema,
        models.ObservabilitySchema.catalog == catalog
    ).order_by(models.ObservabilitySchema.snapshot_time.desc()).first()
    
    if not latest: return []
    
    return db.query(models.ObservabilitySchema).filter(
        models.ObservabilitySchema.table_name == table,
        models.ObservabilitySchema.schema_name == schema,
        models.ObservabilitySchema.catalog == catalog,
        models.ObservabilitySchema.snapshot_time == latest[0]
    ).all()

@router.get("/incidents", response_model=List[schemas.ObservabilityIncident])
def get_incidents(
    table: Optional[str] = Query(None),
    schema: Optional[str] = Query(None),
    db: Session = Depends(deps.get_db)
):
    """Lấy danh sách các bất thường đã phát hiện từ Airflow."""
    query = db.query(models.ObservabilityIncident)
    if table and schema:
        query = query.filter(
            models.ObservabilityIncident.table_name == table,
            models.ObservabilityIncident.schema_name == schema
        )
    return query.order_by(models.ObservabilityIncident.detected_at.desc()).all()

# --- 3. INCIDENT MANAGEMENT ---

@router.put("/incidents/{incident_id}/resolve")
def resolve_incident(
    incident_id: int,
    db: Session = Depends(deps.get_db),
):
    """Đóng cảnh báo."""
    incident = db.query(models.ObservabilityIncident).filter(models.ObservabilityIncident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    incident.status = "resolved"
    db.commit()
    return {"status": "success", "message": f"Incident {incident_id} resolved"}
