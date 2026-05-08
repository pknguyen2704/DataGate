from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID

from app.schemas.common_schema import LightGBMAUCStatus, SeverityLevel


class LightGBMParameterBase(BaseModel):
    table_id: UUID

    learningRate: float = Field(default=0.05, gt=0, le=1)
    numLeaves: int = Field(default=31, gt=1)
    maxDepth: int = -1
    minDataInLeaf: int = Field(default=20, ge=1)

    baggingFraction: float = Field(default=1.0, gt=0, le=1)
    baggingFreq: int = Field(default=0, ge=0)
    featureFraction: float = Field(default=1.0, gt=0, le=1)

    lambdaL1: float = Field(default=1e-8, ge=0)
    lambdaL2: float = Field(default=1e-8, ge=0)
    minGainToSplit: float = Field(default=0.0, ge=0)
    maxBin: int = Field(default=255, gt=1)

    numIterations: int = Field(default=300, gt=0)
    earlyStoppingRound: int = Field(default=30, ge=0)
    useBarrierExecutionMode: bool = True

    is_active: bool = True
    description: str | None = None


class LightGBMParameterCreate(LightGBMParameterBase):
    pass


class LightGBMParameterUpdate(BaseModel):
    learningRate: float | None = Field(default=None, gt=0, le=1)
    numLeaves: int | None = Field(default=None, gt=1)
    maxDepth: int | None = None
    minDataInLeaf: int | None = Field(default=None, ge=1)

    baggingFraction: float | None = Field(default=None, gt=0, le=1)
    baggingFreq: int | None = Field(default=None, ge=0)
    featureFraction: float | None = Field(default=None, gt=0, le=1)

    lambdaL1: float | None = Field(default=None, ge=0)
    lambdaL2: float | None = Field(default=None, ge=0)
    minGainToSplit: float | None = Field(default=None, ge=0)
    maxBin: int | None = Field(default=None, gt=1)

    numIterations: int | None = Field(default=None, gt=0)
    earlyStoppingRound: int | None = Field(default=None, ge=0)
    useBarrierExecutionMode: bool | None = None

    is_active: bool | None = None
    description: str | None = None


class LightGBMParameterOut(LightGBMParameterBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LightGBMAUCManualThresholdBase(BaseModel):
    lightgbm_parameter_id: UUID
    auc_min_threshold: float | None = Field(default=None, ge=0, le=1)
    auc_max_threshold: float | None = Field(default=None, ge=0, le=1)
    severity_level: SeverityLevel = SeverityLevel.WARNING
    is_active: bool = True
    description: str | None = None


class LightGBMAUCManualThresholdCreate(LightGBMAUCManualThresholdBase):
    pass


class LightGBMAUCManualThresholdUpdate(BaseModel):
    auc_min_threshold: float | None = Field(default=None, ge=0, le=1)
    auc_max_threshold: float | None = Field(default=None, ge=0, le=1)
    severity_level: SeverityLevel | None = None
    is_active: bool | None = None
    description: str | None = None


class LightGBMAUCManualThresholdOut(LightGBMAUCManualThresholdBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LightGBMAUCBase(BaseModel):
    lightgbm_parameter_id: UUID
    manual_threshold_id: UUID | None = None
    processing_date_hour: datetime

    auc_score: float | None = Field(default=None, ge=0, le=1)
    status: LightGBMAUCStatus = LightGBMAUCStatus.FAIL

    auc_min_threshold: float | None = Field(default=None, ge=0, le=1)
    auc_max_threshold: float | None = Field(default=None, ge=0, le=1)
    severity_level: SeverityLevel | None = None
    message: str | None = None


class LightGBMAUCCreate(LightGBMAUCBase):
    pass


class LightGBMAUCUpdate(BaseModel):
    manual_threshold_id: UUID | None = None
    auc_score: float | None = Field(default=None, ge=0, le=1)
    status: LightGBMAUCStatus | None = None
    auc_min_threshold: float | None = Field(default=None, ge=0, le=1)
    auc_max_threshold: float | None = Field(default=None, ge=0, le=1)
    severity_level: SeverityLevel | None = None
    message: str | None = None


class LightGBMAUCOut(LightGBMAUCBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


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