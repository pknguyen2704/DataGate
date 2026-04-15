from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.models.profiling import ProfilingRun, ColumnProfile
from app import models
import json
from math import sqrt
from app.api.v1.endpoints.services import get_accessible_asset_service_or_403

router = APIRouter()

CONFIDENCE_Z_MAP = {
    80: 1.2816,
    95: 1.96,
    99: 2.5758,
}


def _resolve_metric_value(profile: ColumnProfile, metric: str):
    metric_map = {
        "maximum": "max",
        "minimum": "min",
        "std_dev": "stddev",
    }
    if metric == "null_rate":
        if profile.completeness is None:
            return None
        return max(0, 1 - profile.completeness)

    db_metric = metric_map.get(metric, metric)
    return getattr(profile, db_metric, None)


def _build_confidence_points(series, confidence: int):
    z_score = CONFIDENCE_Z_MAP.get(confidence, CONFIDENCE_Z_MAP[95])
    enriched = []

    for index, point in enumerate(series):
        history = series[:index]
        seasonal_history = [candidate["value"] for candidate in history if candidate["weekday"] == point["weekday"]]
        baseline = seasonal_history if len(seasonal_history) >= 2 else [candidate["value"] for candidate in history]

        if baseline:
            mean = sum(baseline) / len(baseline)
            if len(baseline) > 1:
                variance = sum((value - mean) ** 2 for value in baseline) / (len(baseline) - 1)
                margin = z_score * sqrt(variance)
            else:
                margin = 0
            lower = mean - margin
            upper = mean + margin
        else:
            mean = point["value"]
            lower = point["value"]
            upper = point["value"]

        enriched.append(
            {
                "created_at": point["created_at"],
                "value": point["value"],
                "expected": mean,
                "lower_bound": lower,
                "upper_bound": upper,
                "is_anomaly": point["value"] < lower or point["value"] > upper,
            }
        )

    return enriched

@router.get("/runs")
def get_profiling_runs(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    runs = db.query(ProfilingRun).order_by(ProfilingRun.batch_time.desc()).all()
    filtered_runs = []
    for run in runs:
        try:
            get_accessible_asset_service_or_403(db, current_user, run.table_name)
            filtered_runs.append(run)
        except HTTPException:
            continue
    return [{
        "id": r.id,
        "table_name": r.table_name,
        "run_time": r.batch_time,
        "batch_id": r.partition_key,
        "num_records": r.num_records,
        "row_count": r.num_records
    } for r in filtered_runs]

@router.get("/runs/{run_id}")
def get_profiling_run_detail(
    run_id: int, 
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    run = db.query(ProfilingRun).filter(ProfilingRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    get_accessible_asset_service_or_403(db, current_user, run.table_name)
    
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
    get_accessible_asset_service_or_403(db, current_user, run.table_name)
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
    get_accessible_asset_service_or_403(db, current_user, table)
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


@router.get("/monitoring/recommendations")
def get_monitoring_recommendations(
    table: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    get_accessible_asset_service_or_403(db, current_user, table)
    latest_run = (
        db.query(ProfilingRun)
        .filter(ProfilingRun.table_name == table)
        .order_by(ProfilingRun.batch_time.desc())
        .first()
    )
    if not latest_run:
        return {"table": table, "recommended_columns": []}

    profiles = (
        db.query(ColumnProfile)
        .filter(ColumnProfile.run_id == latest_run.id)
        .order_by(ColumnProfile.column_name.asc())
        .all()
    )

    def sort_key(profile: ColumnProfile):
        data_type = (profile.data_type or "").lower()
        is_numeric = any(token in data_type for token in ["int", "double", "float", "decimal", "numeric", "real"])
        completeness = profile.completeness if profile.completeness is not None else -1
        return (0 if is_numeric else 1, -completeness, profile.column_name or "")

    recommended = []
    for profile in sorted(profiles, key=sort_key)[:6]:
        metric_cards = [
            {
                "metric": "null_rate",
                "label": "Null rate",
                "value": _resolve_metric_value(profile, "null_rate"),
            },
            {
                "metric": "minimum",
                "label": "Min",
                "value": _resolve_metric_value(profile, "minimum"),
            },
            {
                "metric": "maximum",
                "label": "Max",
                "value": _resolve_metric_value(profile, "maximum"),
            },
        ]
        numeric_type = (profile.data_type or "").lower()
        if any(token in numeric_type for token in ["int", "double", "float", "decimal", "numeric", "real"]):
            metric_cards.extend(
                [
                    {
                        "metric": "mean",
                        "label": "Mean",
                        "value": _resolve_metric_value(profile, "mean"),
                    },
                    {
                        "metric": "std_dev",
                        "label": "Std deviation",
                        "value": _resolve_metric_value(profile, "std_dev"),
                    },
                ]
            )

        recommended.append(
            {
                "column_name": profile.column_name,
                "data_type": profile.data_type,
                "metrics": metric_cards,
            }
        )

    return {"table": table, "recommended_columns": recommended}


@router.get("/monitoring/series")
def get_monitoring_series(
    table: str,
    column: str,
    metric: str = "null_rate",
    confidence: int = 95,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    get_accessible_asset_service_or_403(db, current_user, table)

    runs = (
        db.query(ProfilingRun)
        .filter(ProfilingRun.table_name == table)
        .order_by(ProfilingRun.batch_time.asc())
        .all()
    )
    if not runs:
        return {"table": table, "column": column, "metric": metric, "confidence": confidence, "points": []}

    run_ids = [run.id for run in runs]
    profiles = (
        db.query(ColumnProfile)
        .filter(ColumnProfile.run_id.in_(run_ids), ColumnProfile.column_name == column)
        .order_by(ColumnProfile.run_id.asc())
        .all()
    )
    run_time_map = {run.id: run.batch_time for run in runs}

    raw_series = []
    for profile in profiles:
        value = _resolve_metric_value(profile, metric)
        run_time = run_time_map.get(profile.run_id)
        if value is None or run_time is None:
            continue
        raw_series.append(
            {
                "created_at": run_time.isoformat(),
                "weekday": run_time.weekday(),
                "value": float(value),
            }
        )

    return {
        "table": table,
        "column": column,
        "metric": metric,
        "confidence": confidence,
        "points": _build_confidence_points(raw_series, confidence),
    }
