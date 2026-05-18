from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session, selectinload

from app.models import AnomalyConfig, AnomalyResult, Table
from app.schemas.model_schema import (
    ModelConfigCreate,
    ModelConfigUpdate,
    ModelParameterCreate,
    ModelParameterUpdate,
)


MODEL_PARAMETER_KEYS = {
    "learning_rate",
    "num_leaves",
    "max_depth",
    "min_data_in_leaf",
    "bagging_fraction",
    "bagging_freq",
    "feature_fraction",
    "lambda_l1",
    "lambda_l2",
    "min_gain_to_split",
    "max_bin",
    "num_iterations",
}

FEATURE_CONFIG_KEYS = {
    "required_history_days",
    "previous_batch_hours",
    "history_days",
    "target_sample_per_group",
    "test_size",
    "random_state",
    "p_value_alpha",
    "min_history_auc_points",
}

COLUMN_CONFIG_KEYS = {"exclude_cols", "categorical_cols", "numeric_cols"}


class ModelConfigService:
    def __init__(self, db: Session):
        self.db = db

    def _model_parameter_payload(self, config: AnomalyConfig) -> dict:
        return {
            "id": config.id,
            "table_id": config.table_id,
            **(config.model_parameters or {}),
            "created_at": config.created_at,
            "updated_at": config.updated_at,
            "created_by": config.created_by,
            "last_modified_by": config.last_modified_by,
            "created_by_user": config.created_by_user,
            "last_modified_by_user": config.last_modified_by_user,
        }

    def _anomaly_config_payload(self, config: AnomalyConfig) -> dict:
        return {
            "id": config.id,
            "table_id": config.table_id,
            "batch_time_col": config.batch_time_col,
            **(config.feature_config or {}),
            **(config.column_config or {}),
            "description": config.description,
            "created_at": config.created_at,
            "updated_at": config.updated_at,
            "created_by": config.created_by,
            "last_modified_by": config.last_modified_by,
            "created_by_user": config.created_by_user,
            "last_modified_by_user": config.last_modified_by_user,
        }

    def _auc_result_payload(self, result: AnomalyResult) -> dict:
        return {
            "id": result.id,
            "table_id": result.table_id,
            "model_parameter_id": result.anomaly_config_id,
            "processing_date_hour": result.processing_date_hour,
            "auc_score": result.auc_score,
            "p_value": result.p_value,
            "parameter_snapshot": result.parameter_snapshot,
            "feature_config_snapshot": result.feature_config_snapshot,
            "created_at": result.created_at,
            "updated_at": result.updated_at,
        }

    def _get_table_or_404(self, table_id: str) -> Table:
        table = self.db.query(Table).filter(Table.id == table_id).first()
        if not table:
            raise HTTPException(status_code=404, detail="Table not found")
        return table

    def _get_config_by_table(self, table_id: str) -> AnomalyConfig | None:
        return (
            self.db.query(AnomalyConfig)
            .filter(AnomalyConfig.table_id == table_id)
            .first()
        )

    def _default_feature_config(self) -> dict:
        template = self.get_anomaly_config_template()
        return {key: template[key] for key in FEATURE_CONFIG_KEYS}

    def _default_column_config(self) -> dict:
        template = self.get_anomaly_config_template()
        return {key: template[key] for key in COLUMN_CONFIG_KEYS}

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

    def list_configs(self, page: int = 1, page_size: int = 50) -> dict:
        query = self.db.query(AnomalyConfig).options(
            selectinload(AnomalyConfig.created_by_user),
            selectinload(AnomalyConfig.last_modified_by_user),
        )
        total = query.count()
        items = (
            query.order_by(AnomalyConfig.updated_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return {
            "items": [self._model_parameter_payload(item) for item in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def get_config_or_404(self, config_id: str) -> AnomalyConfig:
        config = self.db.query(AnomalyConfig).filter(AnomalyConfig.id == config_id).first()
        if not config:
            raise HTTPException(status_code=404, detail="Model configuration not found")
        return config

    def get_model_parameter_payload_or_404(self, config_id: str) -> dict:
        return self._model_parameter_payload(self.get_config_or_404(config_id))

    def create_config(self, data: ModelParameterCreate, user_id: str) -> AnomalyConfig:
        table_id = str(data.table_id)
        self._get_table_or_404(table_id)
        existing = self._get_config_by_table(table_id)
        if existing:
            existing.model_parameters = data.model_dump(exclude={"table_id"})
            existing.last_modified_by = user_id
            existing.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(existing)
            return self._model_parameter_payload(existing)
        config = AnomalyConfig(
            table_id=table_id,
            batch_time_col="processing_date_hour",
            feature_config=self._default_feature_config(),
            column_config=self._default_column_config(),
            model_parameters=data.model_dump(exclude={"table_id"}),
            created_by=user_id,
            last_modified_by=user_id,
        )
        self.db.add(config)
        self.db.commit()
        self.db.refresh(config)
        return self._model_parameter_payload(config)

    def update_config(
        self, config_id: str, data: ModelParameterUpdate, user_id: str
    ) -> AnomalyConfig:
        config = self.get_config_or_404(config_id)
        params = dict(config.model_parameters or {})
        params.update(data.model_dump(exclude_unset=True))
        config.model_parameters = params
        config.last_modified_by = user_id
        config.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(config)
        return self._model_parameter_payload(config)

    def delete_config(self, config_id: str) -> None:
        config = self.get_config_or_404(config_id)
        self.db.delete(config)
        self.db.commit()

    def upload_json(self, table_id: str, data: dict, user_id: str) -> AnomalyConfig:
        self._get_table_or_404(table_id)
        template = self.get_template()
        params = {key: data.get(key, default) for key, default in template.items()}
        existing = self._get_config_by_table(table_id)
        if existing:
            existing.model_parameters = params
            existing.last_modified_by = user_id
            existing.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(existing)
            return self._model_parameter_payload(existing)
        config = AnomalyConfig(
            table_id=table_id,
            batch_time_col="processing_date_hour",
            feature_config=self._default_feature_config(),
            model_parameters=params,
            column_config=self._default_column_config(),
            created_by=user_id,
            last_modified_by=user_id,
        )
        self.db.add(config)
        self.db.commit()
        self.db.refresh(config)
        return self._model_parameter_payload(config)

    def list_anomaly_configs(
        self,
        table_id: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> dict:
        query = self.db.query(AnomalyConfig).options(
            selectinload(AnomalyConfig.created_by_user),
            selectinload(AnomalyConfig.last_modified_by_user),
        )
        if table_id:
            query = query.filter(AnomalyConfig.table_id == table_id)
        total = query.count()
        items = (
            query.order_by(AnomalyConfig.updated_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return {
            "items": [self._anomaly_config_payload(item) for item in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def get_anomaly_config_or_404(self, config_id: str) -> AnomalyConfig:
        return self.get_config_or_404(config_id)

    def get_anomaly_config_payload_or_404(self, config_id: str) -> dict:
        return self._anomaly_config_payload(self.get_anomaly_config_or_404(config_id))

    def create_anomaly_config(
        self, data: ModelConfigCreate, user_id: str
    ) -> AnomalyConfig:
        table_id = str(data.table_id)
        self._get_table_or_404(table_id)
        payload = data.model_dump()
        existing = self._get_config_by_table(table_id)
        if existing:
            existing.batch_time_col = payload["batch_time_col"]
            existing.feature_config = {key: payload[key] for key in FEATURE_CONFIG_KEYS}
            existing.column_config = {key: payload[key] for key in COLUMN_CONFIG_KEYS}
            existing.description = payload.get("description")
            existing.last_modified_by = user_id
            existing.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(existing)
            return self._anomaly_config_payload(existing)
        config = AnomalyConfig(
            table_id=table_id,
            batch_time_col=payload["batch_time_col"],
            feature_config={key: payload[key] for key in FEATURE_CONFIG_KEYS},
            column_config={key: payload[key] for key in COLUMN_CONFIG_KEYS},
            model_parameters=self.get_template(),
            description=payload.get("description"),
            created_by=user_id,
            last_modified_by=user_id,
        )
        self.db.add(config)
        self.db.commit()
        self.db.refresh(config)
        return self._anomaly_config_payload(config)

    def update_anomaly_config(
        self, config_id: str, data: ModelConfigUpdate, user_id: str
    ) -> AnomalyConfig:
        config = self.get_anomaly_config_or_404(config_id)
        update_data = data.model_dump(exclude_unset=True)
        feature_config = dict(config.feature_config or {})
        column_config = dict(config.column_config or {})
        for key, value in update_data.items():
            if key == "batch_time_col":
                config.batch_time_col = value
            elif key == "description":
                config.description = value
            elif key in FEATURE_CONFIG_KEYS:
                feature_config[key] = value
            elif key in COLUMN_CONFIG_KEYS:
                column_config[key] = value
        config.feature_config = feature_config
        config.column_config = column_config
        config.last_modified_by = user_id
        config.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(config)
        return self._anomaly_config_payload(config)

    def delete_anomaly_config(self, config_id: str) -> None:
        self.delete_config(config_id)

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
    ) -> AnomalyConfig:
        self._get_table_or_404(table_id)
        template = self.get_anomaly_config_template()
        params = {}
        try:
            for key, default_value in template.items():
                value = data.get(key, default_value)
                if key == "history_days" and isinstance(value, str):
                    value = [int(item.strip()) for item in value.split(",") if item.strip()]
                elif key in COLUMN_CONFIG_KEYS and isinstance(value, str):
                    value = [item.strip() for item in value.split(",") if item.strip()]
                elif key in {
                    "required_history_days",
                    "previous_batch_hours",
                    "target_sample_per_group",
                    "random_state",
                    "min_history_auc_points",
                } and value is not None:
                    value = int(value)
                elif key in {"test_size", "p_value_alpha"} and value is not None:
                    value = float(value)
                params[key] = value
        except (TypeError, ValueError):
            raise HTTPException(status_code=400, detail="Invalid anomaly config JSON values")

        existing = self._get_config_by_table(table_id)
        if existing:
            existing.batch_time_col = params["batch_time_col"]
            existing.feature_config = {key: params[key] for key in FEATURE_CONFIG_KEYS}
            existing.column_config = {key: params[key] for key in COLUMN_CONFIG_KEYS}
            existing.description = params.get("description")
            existing.last_modified_by = user_id
            existing.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(existing)
            return self._anomaly_config_payload(existing)

        config = AnomalyConfig(
            table_id=table_id,
            batch_time_col=params["batch_time_col"],
            feature_config={key: params[key] for key in FEATURE_CONFIG_KEYS},
            column_config={key: params[key] for key in COLUMN_CONFIG_KEYS},
            model_parameters=self.get_template(),
            description=params.get("description"),
            created_by=user_id,
            last_modified_by=user_id,
        )
        self.db.add(config)
        self.db.commit()
        self.db.refresh(config)
        return self._anomaly_config_payload(config)

    def list_auc_results(
        self, table_id: str | None = None, page: int = 1, page_size: int = 50
    ) -> dict:
        query = self.db.query(AnomalyResult)
        if table_id:
            query = query.filter(AnomalyResult.table_id == table_id)
        total = query.count()
        items = (
            query.order_by(AnomalyResult.processing_date_hour.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return {
            "items": [self._auc_result_payload(item) for item in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def get_auc_result_or_404(self, auc_result_id: str) -> AnomalyResult:
        row = self.db.query(AnomalyResult).filter(AnomalyResult.id == auc_result_id).first()
        if not row:
            raise HTTPException(status_code=404, detail="AUC result not found")
        return self._auc_result_payload(row)

    def list_shap_results(self, auc_result_id: str) -> list[dict]:
        row = self.db.query(AnomalyResult).filter(AnomalyResult.id == auc_result_id).first()
        if not row:
            raise HTTPException(status_code=404, detail="AUC result not found")
        return [
            {
                "id": row.id,
                "auc_result_id": row.id,
                "feature_name": item.get("feature_name"),
                "shap_score": item.get("shap_score"),
                "shap_rank": item.get("rank", item.get("shap_rank")),
                "processing_date_hour": row.processing_date_hour,
                "created_at": row.created_at,
                "updated_at": row.updated_at,
            }
            for item in (row.shap_top_features or [])
        ]
