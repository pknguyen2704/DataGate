from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app import models, schemas
from app.api import deps
from app.services.observability_scheduler import (
    build_metadata_profile_conf,
    build_metadata_profile_dag_id,
    cleanup_metadata_profile_dag,
    sync_metadata_profile_dag,
    trigger_airflow_dag,
)
from app.api.v1.endpoints.services import get_accessible_asset_service_or_403

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
    if config.schedule_type == "interval" and not config.interval_minutes:
        raise HTTPException(status_code=400, detail="interval_minutes is required for interval schedules")
    if config.schedule_type == "daily" and (config.hour is None or config.minute is None):
        raise HTTPException(status_code=400, detail="hour and minute are required for daily schedules")

    payload = config.model_dump()
    if payload.get("job_type", "metadata_profile") == "metadata_profile":
      payload["dag_id"] = build_metadata_profile_dag_id(0)

    db_job = models.DQJobConfig(**payload)
    db.add(db_job)
    db.commit()
    db.refresh(db_job)

    if db_job.job_type == "metadata_profile":
        db_job.dag_id = build_metadata_profile_dag_id(db_job.id)
        db.add(db_job)
        db.commit()
        db.refresh(db_job)
        sync_metadata_profile_dag(db_job)

    return db_job

@router.put("/jobs/{job_id}", response_model=schemas.DQJobConfig)
def update_job(
    job_id: int,
    payload: schemas.DQJobConfigUpdate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    job = db.query(models.DQJobConfig).filter(models.DQJobConfig.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(job, field, value)

    if job.schedule_type == "interval" and not job.interval_minutes:
        raise HTTPException(status_code=400, detail="interval_minutes is required for interval schedules")
    if job.schedule_type == "daily" and (job.hour is None or job.minute is None):
        raise HTTPException(status_code=400, detail="hour and minute are required for daily schedules")

    if job.job_type == "metadata_profile":
        job.dag_id = build_metadata_profile_dag_id(job.id)

    db.add(job)
    db.commit()
    db.refresh(job)

    if job.job_type == "metadata_profile":
        if job.is_active:
            sync_metadata_profile_dag(job)
        else:
            cleanup_metadata_profile_dag(job.dag_id)

    return job

@router.delete("/jobs/{job_id}")
def delete_job(
    job_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    job = db.query(models.DQJobConfig).filter(models.DQJobConfig.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    dag_id = job.dag_id
    job_type = job.job_type
    db.delete(job)
    db.commit()

    if job_type == "metadata_profile":
        cleanup_metadata_profile_dag(dag_id)

    return {"status": "success", "message": "Job deleted"}

@router.post("/jobs/{job_id}/trigger")
def trigger_job(
    job_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    job = db.query(models.DQJobConfig).filter(models.DQJobConfig.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    airflow_response = trigger_airflow_dag(job.dag_id or "dq_metadata_collector", build_metadata_profile_conf(job))
    if airflow_response.get("error"):
        raise HTTPException(status_code=502, detail=airflow_response["error"])

    return {"status": "success", "message": "Airflow DAG triggered on-demand", "airflow_response": airflow_response}

@router.post("/trigger-scan")
def trigger_scan_on_demand(
    payload: schemas.DQTriggerOnDemand,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    airflow_response = trigger_airflow_dag(
        "dq_metadata_collector",
        {
            "job_type": "metadata_profile",
            "trigger_type": "manual",
            "catalog": payload.catalog,
            "schema": payload.schema_name,
            "table": payload.table_name,
        },
    )
    if airflow_response.get("error"):
        raise HTTPException(status_code=502, detail=airflow_response["error"])
    return {"status": "success", "message": f"Scan triggered for {payload.table_name}", "airflow_response": airflow_response}

@router.get("/jobs/{job_id}/runs", response_model=List[schemas.DQJobRunHistory])
def get_job_runs(
    job_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    return (
        db.query(models.DQJobRunHistory)
        .filter(models.DQJobRunHistory.job_id == job_id)
        .order_by(models.DQJobRunHistory.created_at.desc())
        .limit(50)
        .all()
    )

@router.get("/snapshots", response_model=List[schemas.DQTableSnapshot])
def get_snapshots(
    table_name: str = None,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    if table_name:
        get_accessible_asset_service_or_403(db, current_user, table_name)
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
    get_accessible_asset_service_or_403(db, current_user, table_name)
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
    get_accessible_asset_service_or_403(db, current_user, table_name)
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
    get_accessible_asset_service_or_403(db, current_user, table_name)
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
    if table_name:
        get_accessible_asset_service_or_403(db, current_user, table_name)
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
        {
            "catalog": catalog,
            "schema": schema,
            "table": table,
            "effective_date": payload.get("effective_date"),
            "sample_size": payload.get("sample_size", 10000),
            "sensitivity": payload.get("sensitivity", "medium"),
        },
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
