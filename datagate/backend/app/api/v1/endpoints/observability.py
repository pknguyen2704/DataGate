from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app import models, schemas
from app.api import deps
from app.services.observability_scheduler import trigger_airflow_dag

router = APIRouter()

@router.get("/jobs", response_model=List[schemas.DQJobConfig])
def get_jobs(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    return db.query(models.DQJobConfig).all()

@router.post("/jobs", response_model=schemas.DQJobConfig)
def create_job(
    config: schemas.DQJobConfigCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    db_job = models.DQJobConfig(**config.model_dump())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

@router.post("/jobs/{job_id}/trigger")
def trigger_job(
    job_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    job = db.query(models.DQJobConfig).filter(models.DQJobConfig.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    trigger_airflow_dag(job)
    return {"status": "success", "message": "Airflow DAG triggered on-demand"}

@router.post("/trigger-scan")
def trigger_scan_on_demand(
    payload: schemas.DQTriggerOnDemand,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """Trigger a scan without a pre-existing job config"""
    from app.models.observability import DQJobConfig
    # Create a temporary config object for the trigger function
    temp_config = DQJobConfig(
        catalog=payload.catalog,
        schema_name=payload.schema_name,
        table_name=payload.table_name,
        id=0 # Indicates on-demand
    )
    trigger_airflow_dag(temp_config)
    return {"status": "success", "message": f"Scan triggered for {payload.table_name}"}

@router.get("/snapshots", response_model=List[schemas.DQTableSnapshot])
def get_snapshots(
    table_name: str = None,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    query = db.query(models.DQTableSnapshot)
    if table_name:
        query = query.filter(or_(
            models.DQTableSnapshot.table_name == table_name,
            models.DQTableSnapshot.table_name.like(f"%.{table_name}")
        ))
    return query.order_by(models.DQTableSnapshot.snapshot_time.desc()).limit(100).all()

@router.get("/volume-ts", response_model=List[schemas.DQTableVolumeTS])
def get_volume_ts(
    table_name: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    return db.query(models.DQTableVolumeTS).filter(or_(
        models.DQTableVolumeTS.table_name == table_name,
        models.DQTableVolumeTS.table_name.like(f"%.{table_name}")
    )).order_by(models.DQTableVolumeTS.dt.asc()).all()

@router.get("/schema", response_model=List[schemas.DQTableSchema])
def get_table_schema(
    table_name: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    # Get the latest snapshot time for schema
    latest_time = db.query(models.DQTableSchema.snapshot_time).filter(or_(
        models.DQTableSchema.table_name == table_name,
        models.DQTableSchema.table_name.like(f"%.{table_name}")
    )).order_by(models.DQTableSchema.snapshot_time.desc()).first()

    if not latest_time:
        return []

    return db.query(models.DQTableSchema).filter(
        or_(
            models.DQTableSchema.table_name == table_name,
            models.DQTableSchema.table_name.like(f"%.{table_name}")
        ),
        models.DQTableSchema.snapshot_time == latest_time[0]
    ).order_by(models.DQTableSchema.column_name.asc()).all()

@router.get("/column-stats", response_model=List[schemas.DQColumnStats])
def get_column_stats(
    table_name: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    # Get the latest snapshot time for this table
    latest_snapshot = db.query(models.DQColumnStats.snapshot_time).filter(or_(
        models.DQColumnStats.table_name == table_name,
        models.DQColumnStats.table_name.like(f"%.{table_name}")
    )).order_by(models.DQColumnStats.snapshot_time.desc()).first()
    
    if not latest_snapshot:
        return []
        
    return db.query(models.DQColumnStats).filter(
        or_(
            models.DQColumnStats.table_name == table_name,
            models.DQColumnStats.table_name.like(f"%.{table_name}")
        ),
        models.DQColumnStats.snapshot_time == latest_snapshot[0]
    ).all()

@router.get("/incidents", response_model=List[schemas.DQIncident])
def get_incidents(
    table_name: str = None,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    query = db.query(models.DQIncident)
    if table_name:
        query = query.filter(or_(
            models.DQIncident.table_name == table_name,
            models.DQIncident.table_name.like(f"%.{table_name}")
        ))
    return query.order_by(models.DQIncident.detected_at.desc()).all()

@router.post("/analyze")
def run_analysis(
    table_name: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    from app.services.observability_analyzer import ObservabilityAnalyzer
    ObservabilityAnalyzer.analyze_table(db, table_name)
    return {"status": "success", "message": f"Analysis triggered for {table_name}"}

@router.post("/ml-trigger")
def trigger_ml_scan(
    payload: dict,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    # Trigger the ml_anomaly_agent DAG in Airflow
    from app.services.observability_scheduler import trigger_airflow_dag
    
    # Fail-safe parsing if table_name is missing but catalog is filled with schema
    catalog = payload.get("catalog", "iceberg")
    schema = payload.get("schema_name", "public")
    table = payload.get("table_name")
    
    if not table and schema:
        # Fallback for old UI format: catalog -> schema, schema_name -> table
        table = schema
        schema = catalog
        catalog = "iceberg"

    res = trigger_airflow_dag(
        "ml_anomaly_agent",
        conf={
            "catalog": catalog,
            "schema": schema,
            "table": table
        }
    )
    return {"status": "triggered", "airflow_response": res}

@router.post("/incidents/internal")
def post_internal_incident(
    incident: schemas.DQIncidentCreate,
    db: Session = Depends(deps.get_db)
) -> Any:
    db_incident = models.DQIncident(**incident.dict())
    db.add(db_incident)
    db.commit()
    db.refresh(db_incident)
    return db_incident
