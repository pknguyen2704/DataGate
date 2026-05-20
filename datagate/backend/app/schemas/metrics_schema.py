from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common_schema import PaginatedResponse, SeverityLevel
from app.schemas.user_schema import UserLiteOut


class MetadataThresholdBase(BaseModel):
    metric_name: str = Field(..., max_length=255)
    min_threshold: float | None = None
    max_threshold: float | None = None
    severity_level: SeverityLevel = SeverityLevel.WARNING
    is_active: bool = True
    description: str | None = None


class MetadataThresholdCreate(MetadataThresholdBase):
    table_id: UUID


class MetadataThresholdUpdate(BaseModel):
    min_threshold: float | None = None
    max_threshold: float | None = None
    severity_level: SeverityLevel | None = None
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


class ProfilingThresholdBase(BaseModel):
    column_name: str = Field(..., max_length=255)
    metric_name: str = Field(..., max_length=255)
    min_threshold: float | None = None
    max_threshold: float | None = None
    severity_level: SeverityLevel = SeverityLevel.WARNING
    is_active: bool = True
    description: str | None = None


class ProfilingThresholdCreate(ProfilingThresholdBase):
    table_id: UUID


class ProfilingThresholdUpdate(BaseModel):
    min_threshold: float | None = None
    max_threshold: float | None = None
    severity_level: SeverityLevel | None = None
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


class AnomalyThresholdBase(BaseModel):
    auc_threshold: float = Field(..., ge=0, le=1)
    severity_level: SeverityLevel = SeverityLevel.WARNING
    is_active: bool = True
    description: str | None = None


class AnomalyThresholdCreate(AnomalyThresholdBase):
    table_id: UUID


class AnomalyThresholdUpdate(BaseModel):
    auc_threshold: float | None = Field(default=None, ge=0, le=1)
    severity_level: SeverityLevel | None = None
    is_active: bool | None = None
    description: str | None = None


class AnomalyThresholdOut(AnomalyThresholdBase):
    id: UUID
    table_id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: UUID | None = None
    last_modified_by: UUID | None = None
    created_by_user: UserLiteOut | None = None
    last_modified_by_user: UserLiteOut | None = None
    model_config = ConfigDict(from_attributes=True)


class AnomalyThresholdListOut(PaginatedResponse[AnomalyThresholdOut]):
    pass
