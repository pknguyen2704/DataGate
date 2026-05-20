from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.models import QualityThreshold, Table
from app.schemas.metrics_schema import (
    AnomalyThresholdCreate,
    AnomalyThresholdUpdate,
    MetadataThresholdCreate,
    MetadataThresholdUpdate,
    ProfilingThresholdCreate,
    ProfilingThresholdUpdate,
)


class MetricsService:
    def __init__(self, db: Session):
        self.db = db

    def _anomaly_threshold_payload(self, threshold: QualityThreshold) -> dict:
        return {
            "id": threshold.id,
            "table_id": threshold.table_id,
            "auc_threshold": threshold.min_threshold,
            "severity_level": threshold.severity_level,
            "is_active": threshold.is_active,
            "description": threshold.description,
            "created_at": threshold.created_at,
            "updated_at": threshold.updated_at,
            "created_by": threshold.created_by,
            "last_modified_by": threshold.last_modified_by,
            "created_by_user": threshold.created_by_user,
            "last_modified_by_user": threshold.last_modified_by_user,
        }

    def _list_thresholds(
        self,
        metric_scope: str,
        table_id: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ):
        query = self.db.query(QualityThreshold).filter(
            QualityThreshold.metric_scope == metric_scope
        )
        if table_id:
            query = query.filter(QualityThreshold.table_id == table_id)

        total = query.count()
        items = (
            query.options(
                joinedload(QualityThreshold.created_by_user),
                joinedload(QualityThreshold.last_modified_by_user),
            )
            .order_by(QualityThreshold.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        if metric_scope == "anomaly":
            items = [self._anomaly_threshold_payload(item) for item in items]
        return {"items": items, "total": total, "page": page, "page_size": page_size}

    def _get_threshold(self, threshold_id: str, metric_scope: str | None = None):
        query = self.db.query(QualityThreshold).filter(QualityThreshold.id == threshold_id)
        if metric_scope:
            query = query.filter(QualityThreshold.metric_scope == metric_scope)
        threshold = query.first()
        if not threshold:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Threshold not found"
            )
        return threshold

    def _validate_table(self, table_id: str) -> None:
        if not self.db.query(Table.id).filter(Table.id == table_id).first():
            raise HTTPException(status_code=404, detail="Table not found")

    def _create_threshold(
        self,
        data,
        metric_scope: str,
        user_id: str,
        column_name: str | None = None,
        metric_name: str | None = None,
        min_threshold: float | None = None,
        max_threshold: float | None = None,
    ):
        table_id = str(data.table_id)
        self._validate_table(table_id)
        metric_name = metric_name or data.metric_name
        existing = (
            self.db.query(QualityThreshold)
            .filter(
                QualityThreshold.table_id == table_id,
                QualityThreshold.metric_scope == metric_scope,
                QualityThreshold.column_name == column_name,
                QualityThreshold.metric_name == metric_name,
            )
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Threshold already exists for this table/metric",
            )

        threshold = QualityThreshold(
            table_id=table_id,
            metric_scope=metric_scope,
            column_name=column_name,
            metric_name=metric_name,
            min_threshold=min_threshold
            if min_threshold is not None
            else getattr(data, "min_threshold", None),
            max_threshold=max_threshold
            if max_threshold is not None
            else getattr(data, "max_threshold", None),
            severity_level=data.severity_level,
            is_active=data.is_active,
            description=data.description,
            created_by=user_id,
            last_modified_by=user_id,
        )
        self.db.add(threshold)
        self.db.commit()
        self.db.refresh(threshold)
        return threshold

    def _update_threshold(self, threshold_id: str, data, metric_scope: str, user_id: str):
        threshold = self._get_threshold(threshold_id, metric_scope)
        update_data = data.model_dump(exclude_unset=True)
        if "auc_threshold" in update_data:
            update_data["min_threshold"] = update_data.pop("auc_threshold")
        for field, value in update_data.items():
            setattr(threshold, field, value)
        threshold.last_modified_by = user_id
        self.db.commit()
        self.db.refresh(threshold)
        return threshold

    def _delete_threshold(self, threshold_id: str, metric_scope: str):
        threshold = self._get_threshold(threshold_id, metric_scope)
        self.db.delete(threshold)
        self.db.commit()

    def list_metadata_thresholds(
        self, table_id: str | None = None, page: int = 1, page_size: int = 50
    ):
        return self._list_thresholds("metadata", table_id, page, page_size)

    def get_metadata_threshold(self, threshold_id: str):
        return self._get_threshold(threshold_id, "metadata")

    def create_metadata_threshold(self, data: MetadataThresholdCreate, user_id: str):
        return self._create_threshold(data, "metadata", user_id)

    def update_metadata_threshold(
        self, threshold_id: str, data: MetadataThresholdUpdate, user_id: str
    ):
        return self._update_threshold(threshold_id, data, "metadata", user_id)

    def delete_metadata_threshold(self, threshold_id: str):
        self._delete_threshold(threshold_id, "metadata")

    def list_profiling_thresholds(
        self, table_id: str | None = None, page: int = 1, page_size: int = 50
    ):
        return self._list_thresholds("profiling", table_id, page, page_size)

    def get_profiling_threshold(self, threshold_id: str):
        return self._get_threshold(threshold_id, "profiling")

    def create_profiling_threshold(self, data: ProfilingThresholdCreate, user_id: str):
        return self._create_threshold(
            data, "profiling", user_id, column_name=data.column_name
        )

    def update_profiling_threshold(
        self, threshold_id: str, data: ProfilingThresholdUpdate, user_id: str
    ):
        return self._update_threshold(threshold_id, data, "profiling", user_id)

    def delete_profiling_threshold(self, threshold_id: str):
        self._delete_threshold(threshold_id, "profiling")

    def list_anomaly_thresholds(
        self, table_id: str | None = None, page: int = 1, page_size: int = 50
    ):
        return self._list_thresholds("anomaly", table_id, page, page_size)

    def get_anomaly_threshold(self, threshold_id: str):
        return self._anomaly_threshold_payload(self._get_threshold(threshold_id, "anomaly"))

    def create_anomaly_threshold(self, data: AnomalyThresholdCreate, user_id: str):
        return self._anomaly_threshold_payload(
            self._create_threshold(
                data,
                "anomaly",
                user_id,
                metric_name="auc_score",
                min_threshold=data.auc_threshold,
            )
        )

    def update_anomaly_threshold(
        self, threshold_id: str, data: AnomalyThresholdUpdate, user_id: str
    ):
        return self._anomaly_threshold_payload(
            self._update_threshold(threshold_id, data, "anomaly", user_id)
        )

    def delete_anomaly_threshold(self, threshold_id: str):
        self._delete_threshold(threshold_id, "anomaly")
