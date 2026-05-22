from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID

from app.schemas.common_schema import SeverityLevel, PaginatedResponse
from app.schemas.user_schema import UserLiteOut


class ModelParameterBase(BaseModel):
    table_id: UUID
    learning_rate: float = Field(default=0.05, gt=0, le=1)
    num_leaves: int = Field(default=31, gt=1)
    max_depth: int = -1
    min_data_in_leaf: int = Field(default=20, ge=1)
    bagging_fraction: float = Field(default=1.0, gt=0, le=1)
    bagging_freq: int = Field(default=0, ge=0)
    feature_fraction: float = Field(default=1.0, gt=0, le=1)
    lambda_l1: float = Field(default=1e-8, ge=0)
    lambda_l2: float = Field(default=1e-8, ge=0)
    min_gain_to_split: float = Field(default=0.0, ge=0)
    max_bin: int = Field(default=255, gt=1)
    num_iterations: int = Field(default=300, gt=0)


class ModelParameterCreate(ModelParameterBase):
    pass


class ModelParameterUpdate(BaseModel):
    learning_rate: float | None = Field(default=None, gt=0, le=1)
    num_leaves: int | None = Field(default=None, gt=1)
    max_depth: int | None = None
    min_data_in_leaf: int | None = Field(default=None, ge=1)
    bagging_fraction: float | None = Field(default=None, gt=0, le=1)
    bagging_freq: int | None = Field(default=None, ge=0)
    feature_fraction: float | None = Field(default=None, gt=0, le=1)
    lambda_l1: float | None = Field(default=None, ge=0)
    lambda_l2: float | None = Field(default=None, ge=0)
    min_gain_to_split: float | None = Field(default=None, ge=0)
    max_bin: int | None = Field(default=None, gt=1)
    num_iterations: int | None = Field(default=None, gt=0)


class ModelParameterOut(ModelParameterBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: UUID | None = None
    last_modified_by: UUID | None = None
    created_by_user: UserLiteOut | None = None
    last_modified_by_user: UserLiteOut | None = None

    model_config = ConfigDict(from_attributes=True)


class ModelParameterListOut(PaginatedResponse[ModelParameterOut]):
    pass


class AnomalyConfigBase(BaseModel):
    table_id: UUID
    batch_time_col: str = Field(..., min_length=1, max_length=255)
    required_history_days: int = Field(..., ge=1)
    previous_batch_hours: int = Field(..., ge=1)
    history_days: list[int] = Field(..., min_length=1)
    target_sample_per_group: int = Field(default=10000, ge=1)
    test_size: float = Field(..., gt=0, lt=1)
    random_state: int = Field(..., ge=0)
    exclude_cols: list[str] = Field(default_factory=list)
    categorical_cols: list[str] = Field(default_factory=list)
    numeric_cols: list[str] = Field(default_factory=list)
    description: str | None = None


class AnomalyConfigCreate(AnomalyConfigBase):
    pass


class AnomalyConfigUpdate(BaseModel):
    batch_time_col: str | None = Field(default=None, min_length=1, max_length=255)
    required_history_days: int | None = Field(default=None, ge=1)
    previous_batch_hours: int | None = Field(default=None, ge=1)
    history_days: list[int] | None = Field(default=None, min_length=1)
    target_sample_per_group: int | None = Field(default=None, ge=1)
    test_size: float | None = Field(default=None, gt=0, lt=1)
    random_state: int | None = Field(default=None, ge=0)
    exclude_cols: list[str] | None = None
    categorical_cols: list[str] | None = None
    numeric_cols: list[str] | None = None
    description: str | None = None


class AnomalyConfigOut(AnomalyConfigBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: UUID | None = None
    last_modified_by: UUID | None = None
    created_by_user: UserLiteOut | None = None
    last_modified_by_user: UserLiteOut | None = None

    model_config = ConfigDict(from_attributes=True)


class AnomalyConfigListOut(PaginatedResponse[AnomalyConfigOut]):
    pass


class AUCManualThresholdBase(BaseModel):
    model_parameter_id: UUID
    auc_threshold: float = Field(..., ge=0, le=1)
    severity_level: SeverityLevel = SeverityLevel.WARNING
    is_active: bool = True
    description: str | None = None


class AUCManualThresholdCreate(AUCManualThresholdBase):
    pass


class AUCManualThresholdUpdate(BaseModel):
    auc_threshold: float | None = Field(default=None, ge=0, le=1)
    severity_level: SeverityLevel | None = None
    is_active: bool | None = None
    description: str | None = None


class AUCManualThresholdOut(AUCManualThresholdBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: UUID | None = None
    last_modified_by: UUID | None = None
    created_by_user: UserLiteOut | None = None
    last_modified_by_user: UserLiteOut | None = None

    model_config = ConfigDict(from_attributes=True)


class AUCResultBase(BaseModel):
    table_id: UUID
    model_parameter_id: UUID
    processing_date_hour: datetime
    auc_score: float | None = Field(default=None, ge=0, le=1)
    parameter_snapshot: dict | None = None
    config_snapshot: dict | None = None


class AUCResultCreate(AUCResultBase):
    pass


class AUCResultUpdate(BaseModel):
    auc_score: float | None = Field(default=None, ge=0, le=1)
    parameter_snapshot: dict | None = None
    config_snapshot: dict | None = None


class AUCResultOut(AUCResultBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AUCResultListOut(PaginatedResponse[AUCResultOut]):
    pass


class SHAPResultBase(BaseModel):
    anomaly_result_id: UUID
    feature_name: str = Field(..., max_length=255)
    shap_score: float
    shap_rank: int
    processing_date_hour: datetime


class SHAPResultCreate(SHAPResultBase):
    pass


class SHAPResultOut(SHAPResultBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
