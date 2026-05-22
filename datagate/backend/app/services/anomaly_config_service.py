from datetime import datetime
from numbers import Real

from fastapi import HTTPException
from sqlalchemy.orm import Session, selectinload

from app.models import AnomalyConfig, AnomalyResult, ModelParameter, SHAPResult, Table
from app.schemas.anomaly_schema import (
    AnomalyConfigCreate,
    AnomalyConfigUpdate,
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
}

COLUMN_CONFIG_KEYS = {"exclude_cols", "categorical_cols", "numeric_cols"}


def _is_number(value) -> bool:
    return isinstance(value, Real) and not isinstance(value, bool)


def _is_int(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


class AnomalyConfigService:
    def __init__(self, db: Session):
        self.db = db

    def _model_parameter_payload(self, config: ModelParameter) -> dict:
        return {
            "id": config.id,
            "table_id": config.table_id,
            "learning_rate": config.learning_rate,
            "num_leaves": config.num_leaves,
            "max_depth": config.max_depth,
            "min_data_in_leaf": config.min_data_in_leaf,
            "bagging_fraction": config.bagging_fraction,
            "bagging_freq": config.bagging_freq,
            "feature_fraction": config.feature_fraction,
            "lambda_l1": config.lambda_l1,
            "lambda_l2": config.lambda_l2,
            "min_gain_to_split": config.min_gain_to_split,
            "max_bin": config.max_bin,
            "num_iterations": config.num_iterations,
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
            "required_history_days": config.required_history_days,
            "previous_batch_hours": config.previous_batch_hours,
            "history_days": config.history_days,
            "target_sample_per_group": config.target_sample_per_group,
            "test_size": config.test_size,
            "random_state": config.random_state,
            "exclude_cols": config.exclude_cols,
            "categorical_cols": config.categorical_cols,
            "numeric_cols": config.numeric_cols,
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
            "model_parameter_id": result.model_parameter_id,
            "processing_date_hour": result.processing_date_hour,
            "auc_score": result.auc_score,
            "parameter_snapshot": result.parameter_snapshot,
            "config_snapshot": result.config_snapshot,
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

    def _get_parameter_by_table(self, table_id: str) -> ModelParameter | None:
        return (
            self.db.query(ModelParameter)
            .filter(ModelParameter.table_id == table_id)
            .first()
        )

    def _validate_json_object(self, data: dict, template: dict, label: str) -> None:
        if not isinstance(data, dict):
            raise HTTPException(
                status_code=400,
                detail=f"{label} JSON must be an object matching the template.",
            )

        expected_keys = set(template.keys())
        actual_keys = set(data.keys())
        missing_keys = sorted(expected_keys - actual_keys)
        unknown_keys = sorted(actual_keys - expected_keys)

        if missing_keys or unknown_keys:
            parts = []
            if missing_keys:
                parts.append(f"missing keys: {', '.join(missing_keys)}")
            if unknown_keys:
                parts.append(f"unknown keys: {', '.join(unknown_keys)}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid {label} JSON format; {'; '.join(parts)}.",
            )

    def _validate_model_parameter_json(self, data: dict) -> dict:
        template = self.get_template()
        self._validate_json_object(data, template, "model parameter")

        int_fields = {
            "num_leaves",
            "max_depth",
            "min_data_in_leaf",
            "bagging_freq",
            "max_bin",
            "num_iterations",
        }
        number_fields = MODEL_PARAMETER_KEYS - int_fields

        for key in sorted(int_fields):
            if not _is_int(data[key]):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid model parameter JSON value: {key} must be an integer.",
                )

        for key in sorted(number_fields):
            if not _is_number(data[key]):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid model parameter JSON value: {key} must be a number.",
                )

        rules = [
            ("learning_rate", data["learning_rate"] > 0 and data["learning_rate"] <= 1, "must be > 0 and <= 1"),
            ("num_leaves", data["num_leaves"] > 1, "must be > 1"),
            ("min_data_in_leaf", data["min_data_in_leaf"] >= 1, "must be >= 1"),
            ("bagging_fraction", data["bagging_fraction"] > 0 and data["bagging_fraction"] <= 1, "must be > 0 and <= 1"),
            ("bagging_freq", data["bagging_freq"] >= 0, "must be >= 0"),
            ("feature_fraction", data["feature_fraction"] > 0 and data["feature_fraction"] <= 1, "must be > 0 and <= 1"),
            ("lambda_l1", data["lambda_l1"] >= 0, "must be >= 0"),
            ("lambda_l2", data["lambda_l2"] >= 0, "must be >= 0"),
            ("min_gain_to_split", data["min_gain_to_split"] >= 0, "must be >= 0"),
            ("max_bin", data["max_bin"] > 1, "must be > 1"),
            ("num_iterations", data["num_iterations"] > 0, "must be > 0"),
        ]
        for key, ok, message in rules:
            if not ok:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid model parameter JSON value: {key} {message}.",
                )

        return {key: data[key] for key in template}

    def _validate_anomaly_config_json(self, data: dict) -> dict:
        template = self.get_anomaly_config_template()
        self._validate_json_object(data, template, "anomaly config")

        string_fields = {"batch_time_col"}
        int_fields = {
            "required_history_days",
            "previous_batch_hours",
            "target_sample_per_group",
            "random_state",
        }
        number_fields = {"test_size"}
        list_int_fields = {"history_days"}
        list_string_fields = COLUMN_CONFIG_KEYS

        for key in sorted(string_fields):
            if not isinstance(data[key], str) or not data[key].strip():
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid anomaly config JSON value: {key} must be a non-empty string.",
                )

        for key in sorted(int_fields):
            if not _is_int(data[key]):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid anomaly config JSON value: {key} must be an integer.",
                )

        for key in sorted(number_fields):
            if not _is_number(data[key]):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid anomaly config JSON value: {key} must be a number.",
                )

        for key in sorted(list_int_fields):
            value = data[key]
            if not isinstance(value, list) or not value or any(not _is_int(item) for item in value):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid anomaly config JSON value: {key} must be a non-empty integer array.",
                )

        for key in sorted(list_string_fields):
            value = data[key]
            if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid anomaly config JSON value: {key} must be a string array.",
                )

        description = data["description"]
        if description is not None and not isinstance(description, str):
            raise HTTPException(
                status_code=400,
                detail="Invalid anomaly config JSON value: description must be a string or null.",
            )

        rules = [
            ("required_history_days", data["required_history_days"] >= 1, "must be >= 1"),
            ("previous_batch_hours", data["previous_batch_hours"] >= 1, "must be >= 1"),
            ("target_sample_per_group", data["target_sample_per_group"] >= 1, "must be >= 1"),
            ("random_state", data["random_state"] >= 0, "must be >= 0"),
            ("test_size", data["test_size"] > 0 and data["test_size"] < 1, "must be > 0 and < 1"),
        ]
        for key, ok, message in rules:
            if not ok:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid anomaly config JSON value: {key} {message}.",
                )

        return {key: data[key] for key in template}

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

    def list_configs(
        self,
        table_id: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> dict:
        query = self.db.query(ModelParameter).options(
            selectinload(ModelParameter.created_by_user),
            selectinload(ModelParameter.last_modified_by_user),
        )
        if table_id:
            query = query.filter(ModelParameter.table_id == table_id)
        total = query.count()
        items = (
            query.order_by(ModelParameter.updated_at.desc())
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

    def get_config_or_404(self, config_id: str) -> ModelParameter:
        config = self.db.query(ModelParameter).filter(ModelParameter.id == config_id).first()
        if not config:
            raise HTTPException(status_code=404, detail="Model configuration not found")
        return config

    def get_model_parameter_payload_or_404(self, config_id: str) -> dict:
        return self._model_parameter_payload(self.get_config_or_404(config_id))

    def create_config(self, data: ModelParameterCreate, user_id: str) -> ModelParameter:
        table_id = str(data.table_id)
        self._get_table_or_404(table_id)
        existing = self._get_parameter_by_table(table_id)
        if existing:
            for key, value in data.model_dump(exclude={"table_id"}).items():
                setattr(existing, key, value)
            existing.last_modified_by = user_id
            existing.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(existing)
            return self._model_parameter_payload(existing)
        config = ModelParameter(
            table_id=table_id,
            **data.model_dump(exclude={"table_id"}),
            created_by=user_id,
            last_modified_by=user_id,
        )
        self.db.add(config)
        self.db.commit()
        self.db.refresh(config)
        return self._model_parameter_payload(config)

    def update_config(
        self, config_id: str, data: ModelParameterUpdate, user_id: str
    ) -> ModelParameter:
        config = self.get_config_or_404(config_id)
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(config, key, value)
        config.last_modified_by = user_id
        config.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(config)
        return self._model_parameter_payload(config)

    def delete_config(self, config_id: str) -> None:
        config = self.get_config_or_404(config_id)
        self.db.delete(config)
        self.db.commit()

    def upload_json(self, table_id: str, data: dict, user_id: str) -> ModelParameter:
        self._get_table_or_404(table_id)
        params = self._validate_model_parameter_json(data)
        existing = self._get_parameter_by_table(table_id)
        if existing:
            for key, value in params.items():
                setattr(existing, key, value)
            existing.last_modified_by = user_id
            existing.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(existing)
            return self._model_parameter_payload(existing)
        config = ModelParameter(
            table_id=table_id,
            **params,
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
        config = self.db.query(AnomalyConfig).filter(AnomalyConfig.id == config_id).first()
        if not config:
            raise HTTPException(status_code=404, detail="Anomaly configuration not found")
        return config

    def get_anomaly_config_payload_or_404(self, config_id: str) -> dict:
        return self._anomaly_config_payload(self.get_anomaly_config_or_404(config_id))

    def create_anomaly_config(
        self, data: AnomalyConfigCreate, user_id: str
    ) -> AnomalyConfig:
        table_id = str(data.table_id)
        self._get_table_or_404(table_id)
        payload = data.model_dump()
        existing = self._get_config_by_table(table_id)
        if existing:
            existing.batch_time_col = payload["batch_time_col"]
            for key in FEATURE_CONFIG_KEYS | COLUMN_CONFIG_KEYS:
                setattr(existing, key, payload[key])
            existing.description = payload.get("description")
            existing.last_modified_by = user_id
            existing.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(existing)
            return self._anomaly_config_payload(existing)
        config = AnomalyConfig(
            table_id=table_id,
            batch_time_col=payload["batch_time_col"],
            **{key: payload[key] for key in FEATURE_CONFIG_KEYS | COLUMN_CONFIG_KEYS},
            description=payload.get("description"),
            created_by=user_id,
            last_modified_by=user_id,
        )
        self.db.add(config)
        self.db.commit()
        self.db.refresh(config)
        return self._anomaly_config_payload(config)

    def update_anomaly_config(
        self, config_id: str, data: AnomalyConfigUpdate, user_id: str
    ) -> AnomalyConfig:
        config = self.get_anomaly_config_or_404(config_id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if key == "batch_time_col":
                config.batch_time_col = value
            elif key == "description":
                config.description = value
            elif key in FEATURE_CONFIG_KEYS or key in COLUMN_CONFIG_KEYS:
                setattr(config, key, value)
        config.last_modified_by = user_id
        config.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(config)
        return self._anomaly_config_payload(config)

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
            "exclude_cols": [],
            "categorical_cols": [],
            "numeric_cols": [],
            "description": None,
        }

    def upload_anomaly_config_json(
        self, table_id: str, data: dict, user_id: str
    ) -> AnomalyConfig:
        self._get_table_or_404(table_id)
        params = self._validate_anomaly_config_json(data)

        existing = self._get_config_by_table(table_id)
        if existing:
            existing.batch_time_col = params["batch_time_col"]
            for key in FEATURE_CONFIG_KEYS | COLUMN_CONFIG_KEYS:
                setattr(existing, key, params[key])
            existing.description = params.get("description")
            existing.last_modified_by = user_id
            existing.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(existing)
            return self._anomaly_config_payload(existing)

        config = AnomalyConfig(
            table_id=table_id,
            batch_time_col=params["batch_time_col"],
            **{key: params[key] for key in FEATURE_CONFIG_KEYS | COLUMN_CONFIG_KEYS},
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

    def list_shap_results(self, anomaly_result_id: str) -> list[dict]:
        row = self.db.query(AnomalyResult).filter(AnomalyResult.id == anomaly_result_id).first()
        if not row:
            raise HTTPException(status_code=404, detail="AUC result not found")
        shap_rows = (
            self.db.query(SHAPResult)
            .filter(SHAPResult.anomaly_result_id == anomaly_result_id)
            .order_by(SHAPResult.shap_rank.asc())
            .all()
        )
        if shap_rows:
            return shap_rows
        return [
            {
                "id": row.id,
                "anomaly_result_id": row.id,
                "feature_name": item.get("feature_name"),
                "shap_score": item.get("shap_score"),
                "shap_rank": item.get("rank", item.get("shap_rank")),
                "processing_date_hour": row.processing_date_hour,
                "created_at": row.created_at,
                "updated_at": row.updated_at,
            }
            for item in (row.shap_top_features or [])
        ]
