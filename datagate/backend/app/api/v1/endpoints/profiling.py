from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.models.profiling import ProfilingRun, ColumnProfile
from app import models
import json

router = APIRouter()

@router.get("/runs")
def get_profiling_runs(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    runs = db.query(ProfilingRun).order_by(ProfilingRun.batch_time.desc()).all()
    return [{
        "id": r.id,
        "table_name": r.table_name,
        "run_time": r.batch_time,
        "batch_id": r.partition_key,
        "num_records": r.num_records,
        "row_count": r.num_records
    } for r in runs]

@router.get("/runs/{run_id}")
def get_profiling_run_detail(
    run_id: int, 
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    run = db.query(ProfilingRun).filter(ProfilingRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    columns = db.query(ColumnProfile).filter(ColumnProfile.run_id == run_id).all()
    
    parsed_columns = []
    for col in columns:
        col_data = {
            "id": col.id,
            "column_name": col.column_name,
            "data_type": col.data_type,
            "completeness": col.completeness,
            "approximateNumDistinctValues": col.approx_distinct,
            "mean": col.mean,
            "minimum": col.min,
            "maximum": col.max,
            "std_dev": col.stddev,
        }
        parsed_columns.append(col_data)

    return {
        "id": run.id,
        "table_name": run.table_name,
        "run_time": run.batch_time,
        "batch_id": run.partition_key,
        "num_records": run.num_records,
        "row_count": run.num_records,
        "columns": parsed_columns
    }

@router.get("/column/{col_profile_id}/histogram")
def get_column_histogram(
    col_profile_id: int, 
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    col_profile = db.query(ColumnProfile).filter(ColumnProfile.id == col_profile_id).first()
    if not col_profile:
        raise HTTPException(status_code=404, detail="Column profile not found")
    
    run = db.query(ProfilingRun).filter(ProfilingRun.id == col_profile.run_id).first()
    full_json = run.raw_json if isinstance(run.raw_json, dict) else json.loads(run.raw_json)
    profiles = full_json.get("profiles", {})
    col_profile_json = profiles.get(col_profile.column_name, {})
    
    histogram_raw = col_profile_json.get("histogram", [])
    
    formatted_hist = []
    if isinstance(histogram_raw, list):
        for entry in histogram_raw:
            formatted_hist.append({
                "bin_value": entry.get("value") or entry.get("bin"),
                "absolute_count": entry.get("count") or entry.get("abs") or 0
            })
    elif isinstance(histogram_raw, dict):
        for k, v in histogram_raw.items():
            formatted_hist.append({"bin_value": k, "absolute_count": v})
            
    return formatted_hist

@router.get("/trend")
def get_profiling_trend(
    table: str, 
    column: str, 
    metric: str = "completeness", 
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    runs = db.query(ProfilingRun).filter(ProfilingRun.table_name == table).order_by(ProfilingRun.batch_time.asc()).all()
    run_ids = [r.id for r in runs]
    
    profiles = db.query(ColumnProfile).filter(
        ColumnProfile.run_id.in_(run_ids),
        ColumnProfile.column_name == column
    ).all()
    
    run_time_map = {r.id: r.batch_time for r in runs}
    
    metric_map = {"maximum": "max", "minimum": "min", "std_dev": "stddev"}
    db_metric = metric_map.get(metric, metric)
    
    trend_data = []
    for p in profiles:
        val = getattr(p, db_metric, None)
        if val is not None:
            trend_data.append({
                "created_at": run_time_map[p.run_id].isoformat(),
                "value": val
            })
            
    return trend_data
