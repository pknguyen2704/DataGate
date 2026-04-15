from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.api import deps
from app.api.v1.endpoints.services import get_accessible_asset_service_or_403

router = APIRouter()


def _table_name_matches(candidate: str | None, requested: str | None) -> bool:
    if not candidate or not requested:
        return False
    return candidate == requested or candidate.endswith(f".{requested}")


def _filter_runs_by_table_name(runs: list[models.MLAnomalyRun], table_name: str | None) -> list[models.MLAnomalyRun]:
    if not table_name:
        return runs
    return [run for run in runs if _table_name_matches(run.table_name, table_name)]

@router.get("/runs", response_model=List[schemas.MLAnomalyRun])
def get_ml_runs(
    db: Session = Depends(deps.get_db),
    table_name: str = None,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    query = db.query(models.MLAnomalyRun)
    if table_name:
        get_accessible_asset_service_or_403(db, current_user, table_name)
    runs = query.order_by(models.MLAnomalyRun.batch_time.desc()).all()
    runs = _filter_runs_by_table_name(runs, table_name)
    if table_name:
        return runs
    return [
        run for run in runs
        if not isinstance(_safe_ml_permission_check(db, current_user, run.table_name), HTTPException)
    ]

@router.get("/runs/{run_id}", response_model=schemas.MLAnomalyRunDetail)
def get_ml_run_detail(
    run_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    run = db.query(models.MLAnomalyRun).filter(models.MLAnomalyRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="ML Run not found")
    get_accessible_asset_service_or_403(db, current_user, run.table_name)
    return run


def _safe_ml_permission_check(db: Session, current_user: models.User, table_name: str):
    try:
        get_accessible_asset_service_or_403(db, current_user, table_name)
        return True
    except HTTPException as exc:
        return exc


@router.post("/runs/internal", response_model=schemas.MLAnomalyRun)
def create_ml_run_internal(
    payload: schemas.MLAnomalyRunCreate,
    db: Session = Depends(deps.get_db),
) -> Any:
    db_run = models.MLAnomalyRun(
        table_name=payload.table_name,
        batch_time=payload.batch_time,
        partition_key=payload.partition_key,
        anomaly_score=payload.anomaly_score,
        status=payload.status,
        raw_json=payload.raw_json,
    )
    db.add(db_run)
    db.commit()
    db.refresh(db_run)

    for feature in payload.features:
        db.add(
            models.MLFeatureImportance(
                run_id=db_run.id,
                column_name=feature.column_name,
                importance_score=feature.importance_score,
            )
        )

    db.commit()
    db.refresh(db_run)
    return db_run
