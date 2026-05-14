from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum as PyEnum
from app.schemas.common_schema import PaginatedResponse
from app.schemas.user_schema import UserLiteOut

class ThresholdSeverity(str, PyEnum):
    WARNING = "warning"
    CRITICAL = "critical"

# Metadata Thresholds
class MetadataThresholdBase(BaseModel):
    metric_name: str
    min_threshold: float | None = None
    max_threshold: float | None = None
    severity_level: ThresholdSeverity = ThresholdSeverity.WARNING
    is_active: bool = True
    description: str | None = None

class MetadataThresholdCreate(MetadataThresholdBase):
    table_id: UUID

class MetadataThresholdUpdate(BaseModel):
    min_threshold: float | None = None
    max_threshold: float | None = None
    severity_level: ThresholdSeverity | None = None
    is_active: bool | None = None
    description: str | None = None

class MetadataThresholdOut(MetadataThresholdBase):
    id: UUID
    table_id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: UUID | None = None
    last_modified_by: UUID | None = None
    created_by_user: UserLiteOut | None = None
    last_modified_by_user: UserLiteOut | None = None
    model_config = ConfigDict(from_attributes=True)

class MetadataThresholdListOut(PaginatedResponse[MetadataThresholdOut]):
    pass

# Profiling Thresholds
class ProfilingThresholdBase(BaseModel):
    column_name: str
    metric_name: str
    min_threshold: float | None = None
    max_threshold: float | None = None
    severity_level: ThresholdSeverity = ThresholdSeverity.WARNING
    is_active: bool = True
    description: str | None = None

class ProfilingThresholdCreate(ProfilingThresholdBase):
    table_id: UUID

class ProfilingThresholdUpdate(BaseModel):
    min_threshold: float | None = None
    max_threshold: float | None = None
    severity_level: ThresholdSeverity | None = None
    is_active: bool | None = None
    description: str | None = None

class ProfilingThresholdOut(ProfilingThresholdBase):
    id: UUID
    table_id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: UUID | None = None
    last_modified_by: UUID | None = None
    created_by_user: UserLiteOut | None = None
    last_modified_by_user: UserLiteOut | None = None
    model_config = ConfigDict(from_attributes=True)

class ProfilingThresholdListOut(PaginatedResponse[ProfilingThresholdOut]):
    pass

# Anomaly Thresholds (AUC)
class AnomalyThresholdBase(BaseModel):
    auc_threshold: float
    severity_level: ThresholdSeverity = ThresholdSeverity.WARNING
    is_active: bool = True
    description: str | None = None

class AnomalyThresholdCreate(AnomalyThresholdBase):
    table_id: UUID

class AnomalyThresholdUpdate(BaseModel):
    auc_threshold: float | None = None
    severity_level: ThresholdSeverity | None = None
    is_active: bool | None = None
    description: str | None = None

class AnomalyThresholdOut(AnomalyThresholdBase):
    id: UUID
    lightgbm_parameter_id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: UUID | None = None
    last_modified_by: UUID | None = None
    created_by_user: UserLiteOut | None = None
    last_modified_by_user: UserLiteOut | None = None
    model_config = ConfigDict(from_attributes=True)

class AnomalyThresholdListOut(PaginatedResponse[AnomalyThresholdOut]):
    pass
