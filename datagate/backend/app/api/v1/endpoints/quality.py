from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app import models, schemas
from app.api import deps
from app.api.v1.endpoints.services import get_accessible_asset_service_or_403
from app.services.notification_service import send_rule_failure_alert

router = APIRouter()

@router.get("/runs", response_model=List[schemas.QualityCheckRun])
def get_quality_runs(
    db: Session = Depends(deps.get_db),
    table_name: str = None,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Get quality check runs history.
    """
    query = db.query(models.QualityCheckRun)
    if table_name:
        get_accessible_asset_service_or_403(db, current_user, table_name)
        query = query.filter(models.QualityCheckRun.table_name == table_name)
    runs = query.order_by(models.QualityCheckRun.batch_time.desc()).all()
    if table_name:
        return runs
    return [
        run for run in runs
        if not isinstance(
            _safe_quality_permission_check(db, current_user, run.table_name),
            HTTPException,
        )
    ]

@router.get("/runs/{run_id}", response_model=schemas.QualityCheckRunDetail)
def get_quality_run_detail(
    run_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Get details of a specific quality check run.
    """
    run = db.query(models.QualityCheckRun).filter(models.QualityCheckRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    get_accessible_asset_service_or_403(db, current_user, run.table_name)
    return run


def _safe_quality_permission_check(db: Session, current_user: models.User, table_name: str):
    try:
        get_accessible_asset_service_or_403(db, current_user, table_name)
        return True
    except HTTPException as exc:
        return exc


def _resolve_rule_for_result(db: Session, table_name: str, result: schemas.QualityCheckResultCreate):
    if result.rule_id:
        return db.query(models.ActiveRule).filter(models.ActiveRule.id == result.rule_id).first()
    return (
        db.query(models.ActiveRule)
        .filter(
            models.ActiveRule.table_name == table_name,
            models.ActiveRule.column_name == result.column_name,
            models.ActiveRule.is_applied.is_(True),
        )
        .order_by(models.ActiveRule.priority.asc(), models.ActiveRule.frequency.desc())
        .first()
    )


@router.post("/runs/internal", response_model=schemas.QualityCheckRun)
def create_quality_run_internal(
    payload: schemas.QualityCheckRunCreate,
    db: Session = Depends(deps.get_db),
) -> Any:
    db_run = models.QualityCheckRun(
        table_name=payload.table_name,
        batch_time=payload.batch_time or datetime.utcnow(),
        partition_key=payload.partition_key,
        total_checks=payload.total_checks,
        failed_checks=payload.failed_checks,
        status=payload.status,
    )
    db.add(db_run)
    db.commit()
    db.refresh(db_run)

    failed_rules: list[dict] = []
    for result in payload.results:
        db_result = models.QualityCheckResult(
            run_id=db_run.id,
            rule_id=result.rule_id,
            column_name=result.column_name,
            rule_type=result.rule_type,
            constraint_status=result.constraint_status,
            constraint_message=result.constraint_message,
            severity=result.severity,
        )
        db.add(db_result)

        db_rule = _resolve_rule_for_result(db, payload.table_name, result)
        if db_rule:
            db_result.rule_id = db_rule.id
            db_rule.last_result_status = result.constraint_status
            db_rule.last_failure_message = result.constraint_message if result.constraint_status.lower() != "success" else None
            db_rule.last_validated_at = db_run.batch_time

        if result.constraint_status.lower() != "success":
            failed_rules.append(
                {
                    "rule_id": result.rule_id,
                    "column_name": result.column_name,
                    "rule_type": result.rule_type,
                    "constraint_message": result.constraint_message,
                }
            )

    db.commit()
    db.refresh(db_run)

    if failed_rules:
        send_rule_failure_alert(payload.table_name, failed_rules)

    return db_run
