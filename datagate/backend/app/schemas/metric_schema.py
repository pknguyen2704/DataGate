from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID

from app.schemas.common_schema import MetricResultStatus, SeverityLevel


class BatchTableMetadataManualThresholdBase(BaseModel):
    table_id: UUID
    metric_name: str = Field(..., max_length=255)
    min_threshold: float | None = None
    max_threshold: float | None = None
    severity_level: SeverityLevel = SeverityLevel.WARNING
    is_active: bool = True
    description: str | None = None


class BatchTableMetadataManualThresholdCreate(BatchTableMetadataManualThresholdBase):
    pass


class BatchTableMetadataManualThresholdUpdate(BaseModel):
    metric_name: str | None = Field(default=None, max_length=255)
    min_threshold: float | None = None
    max_threshold: float | None = None
    severity_level: SeverityLevel | None = None
    is_active: bool | None = None
    description: str | None = None


class BatchTableMetadataManualThresholdOut(BatchTableMetadataManualThresholdBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BatchTableMetadataMetricsVerifyBase(BaseModel):
    metadata_manual_threshold_id: UUID
    batch_table_metadata_id: UUID
    actual_value: float | None = None
    status: MetricResultStatus
    min_threshold: float | None = None
    max_threshold: float | None = None
    severity_level: SeverityLevel | None = None


class BatchTableMetadataMetricsVerifyCreate(BatchTableMetadataMetricsVerifyBase):
    pass


class BatchTableMetadataMetricsVerifyOut(BatchTableMetadataMetricsVerifyBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BatchTableProfilingManualThresholdBase(BaseModel):
    table_id: UUID
    column_name: str = Field(..., max_length=255)
    metric_name: str = Field(..., max_length=255)
    min_threshold: float | None = None
    max_threshold: float | None = None
    severity_level: SeverityLevel = SeverityLevel.WARNING
    is_active: bool = True
    description: str | None = None


class BatchTableProfilingManualThresholdCreate(BatchTableProfilingManualThresholdBase):
    pass


class BatchTableProfilingManualThresholdUpdate(BaseModel):
    column_name: str | None = Field(default=None, max_length=255)
    metric_name: str | None = Field(default=None, max_length=255)
    min_threshold: float | None = None
    max_threshold: float | None = None
    severity_level: SeverityLevel | None = None
    is_active: bool | None = None
    description: str | None = None


class BatchTableProfilingManualThresholdOut(BatchTableProfilingManualThresholdBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BatchTableProfilingMetricsVerifyBase(BaseModel):
    profiling_manual_threshold_id: UUID
    batch_table_profiling_id: UUID
    actual_value: float | None = None
    status: MetricResultStatus
    min_threshold: float | None = None
    max_threshold: float | None = None
    severity_level: SeverityLevel | None = None


class BatchTableProfilingMetricsVerifyCreate(BatchTableProfilingMetricsVerifyBase):
    pass


class BatchTableProfilingMetricsVerifyOut(BatchTableProfilingMetricsVerifyBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
