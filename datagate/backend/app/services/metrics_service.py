from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.models import (
    BatchTableMetadataManualThreshold, 
    BatchTableProfilingManualThreshold,
    LightGBMAUCManualThreshold,
    LightGBMParameter,
    Table
)
from app.schemas.metrics_schema import (
    MetadataThresholdCreate, MetadataThresholdUpdate,
    ProfilingThresholdCreate, ProfilingThresholdUpdate,
    AnomalyThresholdCreate, AnomalyThresholdUpdate
)

class MetricsService:
    def __init__(self, db: Session):
        self.db = db

    # Metadata Thresholds
    def list_metadata_thresholds(self, table_id: str | None = None, page: int = 1, page_size: int = 50):
        query = self.db.query(BatchTableMetadataManualThreshold)
        if table_id:
            query = query.filter(BatchTableMetadataManualThreshold.table_id == table_id)
        
        total = query.count()
        items = (
            query.options(
                joinedload(BatchTableMetadataManualThreshold.created_by_user),
                joinedload(BatchTableMetadataManualThreshold.last_modified_by_user)
            )
            .order_by(BatchTableMetadataManualThreshold.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size
        }

    def get_metadata_threshold(self, threshold_id: str):
        threshold = self.db.query(BatchTableMetadataManualThreshold).filter(BatchTableMetadataManualThreshold.id == threshold_id).first()
        if not threshold:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Threshold not found")
        return threshold

    def create_metadata_threshold(self, data: MetadataThresholdCreate, user_id: str):
        # Check if metric already exists for this table
        existing = self.db.query(BatchTableMetadataManualThreshold).filter(
            BatchTableMetadataManualThreshold.table_id == str(data.table_id),
            BatchTableMetadataManualThreshold.metric_name == data.metric_name
        ).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Metric threshold already exists for this table")

        threshold = BatchTableMetadataManualThreshold(
            **data.model_dump(),
            created_by=user_id,
            last_modified_by=user_id
        )
        self.db.add(threshold)
        self.db.commit()
        self.db.refresh(threshold)
        return threshold

    def update_metadata_threshold(self, threshold_id: str, data: MetadataThresholdUpdate, user_id: str):
        threshold = self.get_metadata_threshold(threshold_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(threshold, field, value)
        threshold.last_modified_by = user_id
        self.db.commit()
        self.db.refresh(threshold)
        return threshold

    def delete_metadata_threshold(self, threshold_id: str):
        threshold = self.get_metadata_threshold(threshold_id)
        self.db.delete(threshold)
        self.db.commit()

    # Profiling Thresholds
    def list_profiling_thresholds(self, table_id: str | None = None, page: int = 1, page_size: int = 50):
        query = self.db.query(BatchTableProfilingManualThreshold)
        if table_id:
            query = query.filter(BatchTableProfilingManualThreshold.table_id == table_id)
            
        total = query.count()
        items = (
            query.options(
                joinedload(BatchTableProfilingManualThreshold.created_by_user),
                joinedload(BatchTableProfilingManualThreshold.last_modified_by_user)
            )
            .order_by(BatchTableProfilingManualThreshold.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size
        }

    def get_profiling_threshold(self, threshold_id: str):
        threshold = self.db.query(BatchTableProfilingManualThreshold).filter(BatchTableProfilingManualThreshold.id == threshold_id).first()
        if not threshold:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Threshold not found")
        return threshold

    def create_profiling_threshold(self, data: ProfilingThresholdCreate, user_id: str):
        existing = self.db.query(BatchTableProfilingManualThreshold).filter(
            BatchTableProfilingManualThreshold.table_id == str(data.table_id),
            BatchTableProfilingManualThreshold.column_name == data.column_name,
            BatchTableProfilingManualThreshold.metric_name == data.metric_name
        ).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Profiling threshold already exists for this column/metric")

        threshold = BatchTableProfilingManualThreshold(
            **data.model_dump(),
            created_by=user_id,
            last_modified_by=user_id
        )
        self.db.add(threshold)
        self.db.commit()
        self.db.refresh(threshold)
        return threshold

    def update_profiling_threshold(self, threshold_id: str, data: ProfilingThresholdUpdate, user_id: str):
        threshold = self.get_profiling_threshold(threshold_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(threshold, field, value)
        threshold.last_modified_by = user_id
        self.db.commit()
        self.db.refresh(threshold)
        return threshold

    def delete_profiling_threshold(self, threshold_id: str):
        threshold = self.get_profiling_threshold(threshold_id)
        self.db.delete(threshold)
        self.db.commit()

    # Anomaly Thresholds
    def list_anomaly_thresholds(self, table_id: str | None = None, page: int = 1, page_size: int = 50):
        query = self.db.query(LightGBMAUCManualThreshold)
        if table_id:
            query = query.join(LightGBMParameter).filter(LightGBMParameter.table_id == table_id)
            
        total = query.count()
        items = (
            query.options(
                joinedload(LightGBMAUCManualThreshold.created_by_user),
                joinedload(LightGBMAUCManualThreshold.last_modified_by_user)
            )
            .order_by(LightGBMAUCManualThreshold.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size
        }

    def get_anomaly_threshold(self, threshold_id: str):
        threshold = self.db.query(LightGBMAUCManualThreshold).filter(LightGBMAUCManualThreshold.id == threshold_id).first()
        if not threshold:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Threshold not found")
        return threshold

    def create_anomaly_threshold(self, data: AnomalyThresholdCreate, user_id: str):
        # Find or create LightGBMParameter for table
        lgbm_param = self.db.query(LightGBMParameter).filter(LightGBMParameter.table_id == str(data.table_id)).first()
        if not lgbm_param:
            # Create default parameters if missing
            lgbm_param = LightGBMParameter(
                table_id=str(data.table_id),
                learning_rate=0.01,
                num_leaves=31,
                max_depth=-1,
                min_data_in_leaf=20,
                bagging_fraction=0.8,
                bagging_freq=5,
                feature_fraction=0.8,
                lambda_l1=0.0,
                lambda_l2=0.0,
                min_gain_to_split=0.0,
                max_bin=255,
                num_iterations=100,
                created_by=user_id,
                last_modified_by=user_id
            )
            self.db.add(lgbm_param)
            self.db.flush()

        threshold = LightGBMAUCManualThreshold(
            lightgbm_parameter_id=lgbm_param.id,
            auc_threshold=data.auc_threshold,
            severity_level=data.severity_level,
            description=data.description,
            is_active=data.is_active,
            created_by=user_id,
            last_modified_by=user_id
        )
        self.db.add(threshold)
        self.db.commit()
        self.db.refresh(threshold)
        return threshold

    def update_anomaly_threshold(self, threshold_id: str, data: AnomalyThresholdUpdate, user_id: str):
        threshold = self.get_anomaly_threshold(threshold_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(threshold, field, value)
        threshold.last_modified_by = user_id
        self.db.commit()
        self.db.refresh(threshold)
        return threshold

    def delete_anomaly_threshold(self, threshold_id: str):
        threshold = self.get_anomaly_threshold(threshold_id)
        self.db.delete(threshold)
        self.db.commit()
