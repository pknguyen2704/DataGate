from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common_schema import PaginatedResponse


class ResultType(str, Enum):
    METADATA = "metadata"
    PROFILING = "profiling"
    RULE = "rule"
    ANOMALY = "anomaly"


class QualityResultOut(BaseModel):
    id: UUID
    result_type: ResultType
    table_id: UUID
    table_name: str | None = None
    column_name: str | None = None
    metric_name: str | None = None
    status: str
    severity_level: str | None = None
    actual_value: float | None = None
    threshold_value: float | None = None
    message: str | None = None
    is_resolved: bool
    processing_date_hour: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class QualityResultListOut(PaginatedResponse[QualityResultOut]):
    pass


class DataQualitySummary(BaseModel):
    total_checks: int
    total_pass: int
    total_fail: int
    unresolved_alerts: int
    warning_fail: int
    critical_fail: int
    pass_rate: float
    checks_by_type: dict


class MetadataResultDetail(BaseModel):
    id: UUID
    table_id: UUID
    table_name: str | None = None
    result_type: ResultType | None = None
    metric_name: str
    status: str
    severity_level: str | None = None
    actual_value: float | None = None
    threshold_value: float | None = None
    min_threshold: float | None = None
    max_threshold: float | None = None
    description: str | None = None
    is_resolved: bool
    processing_date_hour: datetime
    created_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


class ProfilingResultDetail(BaseModel):
    id: UUID
    table_id: UUID
    table_name: str | None = None
    result_type: ResultType | None = None
    column_name: str
    metric_name: str
    status: str
    severity_level: str | None = None
    actual_value: float | None = None
    threshold_value: float | None = None
    min_threshold: float | None = None
    max_threshold: float | None = None
    description: str | None = None
    is_resolved: bool
    processing_date_hour: datetime
    created_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


class RuleResultDetail(BaseModel):
    id: UUID
    rule_id: UUID | None = None
    table_id: UUID
    table_name: str | None = None
    result_type: ResultType | None = None
    column_name: str | None = None
    constraint_name: str | None = None
    code_for_constraint: str | None = None
    rule_description: str | None = None
    severity_level: str | None = None
    processing_date_hour: datetime | None = None
    status: str
    message: str | None = None
    is_resolved: bool
    created_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


class AnomalyResultDetail(BaseModel):
    id: UUID
    table_id: UUID
    status: str
    severity_level: str
    processing_date_hour: datetime
    is_resolved: bool
    auc_score: float | None = None
    auc_threshold: float | None = None
    model_config_params: dict | None = None
    top_features: list[dict] = Field(default_factory=list)
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
