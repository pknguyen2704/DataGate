from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.api import deps

router = APIRouter()

@router.get("/runs", response_model=List[schemas.MLAnomalyRun])
def get_ml_runs(
    db: Session = Depends(deps.get_db),
    table_name: str = None,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    query = db.query(models.MLAnomalyRun)
    if table_name:
        query = query.filter(models.MLAnomalyRun.table_name == table_name)
    return query.order_by(models.MLAnomalyRun.batch_time.desc()).all()

@router.get("/runs/{run_id}", response_model=schemas.MLAnomalyRunDetail)
def get_ml_run_detail(
    run_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    run = db.query(models.MLAnomalyRun).filter(models.MLAnomalyRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="ML Run not found")
    return run
