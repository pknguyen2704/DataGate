from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import BatchTableMetadataManualThreshold, BatchTableProfilingManualThreshold, LightGBMAUCManualThreshold


class MetricService:
    def __init__(self, db: Session):
        self.db = db

    def _model(self, metric_type: str):
        return {
            "metadata": BatchTableMetadataManualThreshold,
            "profiling": BatchTableProfilingManualThreshold,
            "auc": LightGBMAUCManualThreshold,
        }[metric_type]

    def list_thresholds(self, metric_type: str):
        return self.db.query(self._model(metric_type)).order_by(self._model(metric_type).updated_at.desc()).all()

    def get_threshold_or_404(self, metric_type: str, threshold_id: str):
        row = self.db.query(self._model(metric_type)).filter(self._model(metric_type).id == threshold_id).first()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Threshold not found")
        return row

    def create_threshold(self, metric_type: str, data, user_id: str):
        row = self._model(metric_type)(**data.model_dump(), created_by=user_id, last_modified_by=user_id)
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def update_threshold(self, metric_type: str, threshold_id: str, data, user_id: str):
        row = self.get_threshold_or_404(metric_type, threshold_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(row, field, value)
        row.last_modified_by = user_id
        self.db.commit()
        self.db.refresh(row)
        return row

    def delete_threshold(self, metric_type: str, threshold_id: str) -> None:
        row = self.get_threshold_or_404(metric_type, threshold_id)
        if hasattr(row, "is_active"):
            row.is_active = False
        else:
            self.db.delete(row)
        self.db.commit()

    def set_active(self, metric_type: str, threshold_id: str, active: bool, user_id: str):
        row = self.get_threshold_or_404(metric_type, threshold_id)
        if not hasattr(row, "is_active"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This threshold type has no active flag")
        row.is_active = active
        row.last_modified_by = user_id
        self.db.commit()
        self.db.refresh(row)
        return row
