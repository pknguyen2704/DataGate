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


class HomeSummaryOut(BaseModel):
    total_tables: int
    total_pass: int
    total_fail: int
    warning_fail: int
    critical_fail: int
    unresolved_alerts: int
