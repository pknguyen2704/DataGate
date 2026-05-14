from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from typing import Any, List, Optional
from enum import Enum
from app.schemas.common_schema import PaginatedResponse, SeverityLevel, MetricResultStatus

class ResultType(str, Enum):
    METADATA = "metadata"
    PROFILING = "profiling"
    RULE = "rule"
    ANOMALY = "anomaly"


class QualityResultOut(BaseModel):
    id: UUID
    result_type: str  # metadata, profiling, rule, anomaly
    table_id: UUID
    column_name: Optional[str] = None
    metric_name: Optional[str] = None
    status: str
    severity_level: Optional[str] = None
    actual_value: Optional[float] = None
    threshold_value: Optional[float] = None
    message: Optional[str] = None
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
    metric_name: str
    status: str
    severity_level: str
    actual_value: float
    threshold_value: float
    is_resolved: bool
    processing_date_hour: datetime
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ProfilingResultDetail(BaseModel):
    id: UUID
    table_id: UUID
    column_name: str
    metric_name: str
    status: str
    severity_level: str
    actual_value: float
    threshold_value: float
    is_resolved: bool
    processing_date_hour: datetime
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class RuleResultDetail(BaseModel):
    id: UUID
    rule_id: UUID
    table_id: UUID
    column_name: Optional[str] = None
    status: str
    message: Optional[str] = None
    is_resolved: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class AnomalyResultDetail(BaseModel):
    id: UUID
    table_id: UUID
    status: str
    severity_level: str
    processing_date_hour: datetime
    is_resolved: bool
    auc_score: float
    auc_threshold: float
    model_config_params: Optional[dict] = None
    top_features: List[dict] = []
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
