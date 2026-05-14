from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID

from app.schemas.common_schema import LightGBMAUCStatus, SeverityLevel, PaginatedResponse


class LightGBMParameterBase(BaseModel):
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


class LightGBMParameterCreate(LightGBMParameterBase):
    pass


class LightGBMParameterUpdate(BaseModel):
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


class LightGBMParameterOut(LightGBMParameterBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LightGBMParameterListOut(PaginatedResponse[LightGBMParameterOut]):
    pass


class LightGBMAUCManualThresholdBase(BaseModel):
    lightgbm_parameter_id: UUID
    auc_threshold: float = Field(..., ge=0, le=1)
    severity_level: SeverityLevel = SeverityLevel.WARNING
    description: str | None = None


class LightGBMAUCManualThresholdCreate(LightGBMAUCManualThresholdBase):
    pass


class LightGBMAUCManualThresholdUpdate(BaseModel):
    auc_threshold: float | None = Field(default=None, ge=0, le=1)
    severity_level: SeverityLevel | None = None
    description: str | None = None


class LightGBMAUCManualThresholdOut(LightGBMAUCManualThresholdBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LightGBMAUCBase(BaseModel):
    table_id: UUID
    lightgbm_parameter_id: UUID
    processing_date_hour: datetime
    auc_score: float | None = Field(default=None, ge=0, le=1)
    p_value: float | None = None
    parameter_snapshot: dict | None = None


class LightGBMAUCCreate(LightGBMAUCBase):
    pass


class LightGBMAUCUpdate(BaseModel):
    auc_score: float | None = Field(default=None, ge=0, le=1)
    p_value: float | None = None
    parameter_snapshot: dict | None = None


class LightGBMAUCOut(LightGBMAUCBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LightGBMAUCListOut(PaginatedResponse[LightGBMAUCOut]):
    pass


class SHAPResultBase(BaseModel):
    lightgbm_result_id: UUID
    feature_name: str = Field(..., max_length=255)
    shap_score: float
    shap_rank: int | None = None


class SHAPResultCreate(SHAPResultBase):
    pass


class SHAPResultOut(SHAPResultBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
