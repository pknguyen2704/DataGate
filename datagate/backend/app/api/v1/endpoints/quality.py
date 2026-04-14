from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.api import deps

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
        query = query.filter(models.QualityCheckRun.table_name == table_name)
    return query.order_by(models.QualityCheckRun.batch_time.desc()).all()

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
    return run
