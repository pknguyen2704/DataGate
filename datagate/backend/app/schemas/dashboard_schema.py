from datetime import datetime
from pydantic import BaseModel


class PlatformOverviewOut(BaseModel):
    total_tables: int
    latest_batch: datetime | None


class TimelineStatsOut(BaseModel):
    processing_date_hour: datetime
    pass_critical: int
    pass_warning: int
    fail_critical: int
    fail_warning: int


class SchemaHealthOut(BaseModel):
    schema_name: str
    table_count: int = 0
    critical_fail_count: int = 0
    warning_fail_count: int = 0
    total_check_count: int = 0


class TableHealthOut(BaseModel):
    table_id: str
    schema_name: str
    table_name: str
    critical_fail_count: int = 0
    warning_fail_count: int = 0
    total_check_count: int = 0
    status: str

class FailureSummaryOut(BaseModel):
    critical_fail_count: int
    warning_fail_count: int
    total_fail_count: int


class ManagedTableNodeOut(BaseModel):
    table_id: str
    table_name: str


class ConnectionVarOut(BaseModel):
    id: str
    name: str

class ManagedSchemaNodeOut(BaseModel):
    schema_name: str
    tables: list[ManagedTableNodeOut]


class GrafanaVariablesOut(BaseModel):
    catalogs: list[str]
    schemas: list[str]
    tables: list[str]
    connections: list[ConnectionVarOut] = []
    processing_date_hours: list[datetime]


class GrafanaEmbedUrlOut(BaseModel):
    url: str


class TimeRangeOut(BaseModel):
    default_from: datetime | None
    default_to: datetime | None


class QualityResultOut(BaseModel):
    id: str
    result_type: str
    status: str
    severity_level: str | None = None
    is_resolved: bool
    processing_date_hour: datetime


class HomeSummaryOut(BaseModel):
    total_tables: int
    total_pass: int
    total_fail: int
    warning_fail: int
    critical_fail: int
    unresolved_alerts: int
