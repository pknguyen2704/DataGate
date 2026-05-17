from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.models import ModelConfig, ModelParameter, Table, AUCResult, SHAPResult
from app.schemas.model_schema import (
    ModelConfigCreate,
    ModelConfigUpdate,
    ModelParameterCreate,
    ModelParameterUpdate,
)


class ModelConfigService:
    def __init__(self, db: Session):
        self.db = db

    def list_configs(self, page: int = 1, page_size: int = 50) -> dict:
        from sqlalchemy.orm import selectinload

        query = self.db.query(ModelParameter).options(
            selectinload(ModelParameter.created_by_user),
            selectinload(ModelParameter.last_modified_by_user),
        )
        total = query.count()
        items = (
            query.order_by(ModelParameter.updated_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return {"items": items, "total": total, "page": page, "page_size": page_size}

    def get_config_or_404(self, config_id: str) -> ModelParameter:
        config = (
            self.db.query(ModelParameter).filter(ModelParameter.id == config_id).first()
        )
        if not config:
            raise HTTPException(status_code=404, detail="Model configuration not found")
        return config

    def create_config(self, data: ModelParameterCreate, user_id: str) -> ModelParameter:
        # Check if table already has a config
        existing = (
            self.db.query(ModelParameter)
            .filter(ModelParameter.table_id == str(data.table_id))
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Configuration already exists for this table. Use update instead.",
            )

        config = ModelParameter(
            **data.model_dump(), created_by=user_id, last_modified_by=user_id
        )
        self.db.add(config)
        self.db.commit()
        self.db.refresh(config)
        return config

    def update_config(
        self, config_id: str, data: ModelParameterUpdate, user_id: str
    ) -> ModelParameter:
        config = self.get_config_or_404(config_id)
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(config, field, value)
        config.last_modified_by = user_id
        config.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(config)
        return config

    def delete_config(self, config_id: str) -> None:
        config = self.get_config_or_404(config_id)
        self.db.delete(config)
        self.db.commit()

    def get_template(self) -> dict:
        return {
            "learning_rate": 0.05,
            "num_leaves": 31,
            "max_depth": -1,
            "min_data_in_leaf": 20,
            "bagging_fraction": 0.8,
            "bagging_freq": 5,
            "feature_fraction": 0.8,
            "lambda_l1": 0.0,
            "lambda_l2": 0.0,
            "min_gain_to_split": 0.0,
            "max_bin": 255,
            "num_iterations": 100,
        }

    def upload_json(self, table_id: str, data: dict, user_id: str) -> ModelParameter:
        # Validate table exists
        table = self.db.query(Table).filter(Table.id == table_id).first()
        if not table:
            raise HTTPException(status_code=404, detail="Table not found")

        # Extract fields
        template = self.get_template()
        params = {}
        for key in template.keys():
            if key in data:
                params[key] = data[key]
            else:
                params[key] = template[key]

        # Check if already exists
        existing = (
            self.db.query(ModelParameter)
            .filter(ModelParameter.table_id == table_id)
            .first()
        )
        if existing:
            for field, value in params.items():
                setattr(existing, field, value)
            existing.last_modified_by = user_id
            existing.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            config = ModelParameter(
                table_id=table_id,
                **params,
                created_by=user_id,
                last_modified_by=user_id,
            )
            self.db.add(config)
            self.db.commit()
            self.db.refresh(config)
            return config

    def list_anomaly_configs(
        self,
        table_id: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> dict:
        from sqlalchemy.orm import selectinload

        query = self.db.query(ModelConfig).options(
            selectinload(ModelConfig.created_by_user),
            selectinload(ModelConfig.last_modified_by_user),
        )
        if table_id:
            query = query.filter(ModelConfig.table_id == table_id)

        total = query.count()
        items = (
            query.order_by(ModelConfig.updated_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def get_anomaly_config_or_404(self, config_id: str) -> ModelConfig:
        config = self.db.query(ModelConfig).filter(ModelConfig.id == config_id).first()
        if not config:
            raise HTTPException(
                status_code=404, detail="Anomaly job configuration not found"
            )
        return config

    def create_anomaly_config(
        self,
        data: ModelConfigCreate,
        user_id: str,
    ) -> ModelConfig:
        table = self.db.query(Table).filter(Table.id == str(data.table_id)).first()
        if not table:
            raise HTTPException(status_code=404, detail="Table not found")

        existing = (
            self.db.query(ModelConfig)
            .filter(ModelConfig.table_id == str(data.table_id))
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Anomaly job configuration already exists for this table. Use update instead.",
            )

        config = ModelConfig(
            **data.model_dump(),
            created_by=user_id,
            last_modified_by=user_id,
        )
        self.db.add(config)
        self.db.commit()
        self.db.refresh(config)
        return config

    def update_anomaly_config(
        self,
        config_id: str,
        data: ModelConfigUpdate,
        user_id: str,
    ) -> ModelConfig:
        config = self.get_anomaly_config_or_404(config_id)
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(config, field, value)
        config.last_modified_by = user_id
        config.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(config)
        return config

    def delete_anomaly_config(self, config_id: str) -> None:
        config = self.get_anomaly_config_or_404(config_id)
        self.db.delete(config)
        self.db.commit()

    def get_anomaly_config_template(self) -> dict:
        return {
            "batch_time_col": "processing_date_hour",
            "required_history_days": 30,
            "previous_batch_hours": 24,
            "history_days": [7, 14, 30],
            "target_sample_per_group": 10000,
            "test_size": 0.2,
            "random_state": 42,
            "p_value_alpha": 0.05,
            "min_history_auc_points": 20,
            "exclude_cols": [],
            "categorical_cols": [],
            "numeric_cols": [],
            "description": None,
        }

    def upload_anomaly_config_json(
        self, table_id: str, data: dict, user_id: str
    ) -> ModelConfig:
        table = self.db.query(Table).filter(Table.id == table_id).first()
        if not table:
            raise HTTPException(status_code=404, detail="Table not found")

        template = self.get_anomaly_config_template()
        integer_fields = {
            "required_history_days",
            "previous_batch_hours",
            "target_sample_per_group",
            "random_state",
            "min_history_auc_points",
        }
        float_fields = {"test_size", "p_value_alpha"}
        params = {}
        try:
            for key, default_value in template.items():
                value = data.get(key, default_value)
                if key == "history_days" and isinstance(value, str):
                    value = [
                        int(item.strip()) for item in value.split(",") if item.strip()
                    ]
                elif key in {
                    "exclude_cols",
                    "categorical_cols",
                    "numeric_cols",
                } and isinstance(value, str):
                    value = [item.strip() for item in value.split(",") if item.strip()]
                elif key in integer_fields and value is not None:
                    value = int(value)
                elif key in float_fields and value is not None:
                    value = float(value)
                params[key] = value
        except (TypeError, ValueError):
            raise HTTPException(
                status_code=400, detail="Invalid anomaly config JSON values"
            )

        existing = (
            self.db.query(ModelConfig).filter(ModelConfig.table_id == table_id).first()
        )
        if existing:
            for field, value in params.items():
                setattr(existing, field, value)
            existing.last_modified_by = user_id
            existing.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(existing)
            return existing

        config = ModelConfig(
            table_id=table_id,
            **params,
            created_by=user_id,
            last_modified_by=user_id,
        )
        self.db.add(config)
        self.db.commit()
        self.db.refresh(config)
        return config

    # Merged methods from AnomalyDetectionService
    def list_auc_results(
        self, table_id: str | None = None, page: int = 1, page_size: int = 50
    ) -> dict:
        query = self.db.query(AUCResult)
        if table_id:
            query = query.filter(AUCResult.table_id == table_id)

        total = query.count()
        items = (
            query.order_by(AUCResult.processing_date_hour.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return {"items": items, "total": total, "page": page, "page_size": page_size}

    def get_auc_result_or_404(self, auc_result_id: str) -> AUCResult:
        row = self.db.query(AUCResult).filter(AUCResult.id == auc_result_id).first()
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="AUC result not found"
            )
        return row

    def list_shap_results(self, auc_result_id: str) -> list[SHAPResult]:
        self.get_auc_result_or_404(auc_result_id)
        return (
            self.db.query(SHAPResult)
            .filter(SHAPResult.auc_result_id == auc_result_id)
            .order_by(SHAPResult.shap_rank.asc())
            .all()
        )
