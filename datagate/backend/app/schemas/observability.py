from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime, date

class DQJobConfigBase(BaseModel):
    catalog: str
    schema_name: str
    table_name: str
    schedule_type: str = "daily"
    interval_minutes: Optional[int] = None
    hour: Optional[int] = None
    minute: Optional[int] = None
    dag_id: str = "dq_metadata_collector"
    job_type: str = "metadata_profile"
    is_active: bool = True

class DQJobConfigCreate(DQJobConfigBase):
    pass

class DQJobConfigUpdate(BaseModel):
    catalog: Optional[str] = None
    schema_name: Optional[str] = None
    table_name: Optional[str] = None
    schedule_type: Optional[str] = None
    interval_minutes: Optional[int] = None
    hour: Optional[int] = None
    minute: Optional[int] = None
    dag_id: Optional[str] = None
    job_type: Optional[str] = None
    is_active: Optional[bool] = None

class DQJobConfig(DQJobConfigBase):
    id: int
    last_run_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class DQJobRunHistoryBase(BaseModel):
    job_id: int
    dag_id: Optional[str] = None
    dag_run_id: Optional[str] = None
    trigger_type: str = "scheduled"
    status: str = "queued"
    scheduled_for: Optional[datetime] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    error_message: Optional[str] = None

class DQJobRunHistory(DQJobRunHistoryBase):
    id: int
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class DQTableSnapshotBase(BaseModel):
    table_name: str
    snapshot_time: datetime
    last_updated_time: Optional[datetime] = None
    total_records: Optional[int] = None
    total_size: Optional[int] = None

class DQTableSnapshot(DQTableSnapshotBase):
    id: int
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class DQTableVolumeTSBase(BaseModel):
    table_name: str
    dt: date
    records_added: Optional[int] = 0

class DQTableVolumeTS(DQTableVolumeTSBase):
    id: int
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class DQTriggerOnDemand(BaseModel):
    catalog: str
    schema_name: str
    table_name: str

class DQTableSchemaBase(BaseModel):
    table_name: str
    column_name: str
    data_type: str
    snapshot_time: datetime

class DQTableSchema(DQTableSchemaBase):
    id: int
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class DQColumnStatsBase(BaseModel):
    table_name: str
    column_name: str
    nulls: int
    total: int
    snapshot_time: datetime

class DQColumnStats(DQColumnStatsBase):
    id: int
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class DQIncidentBase(BaseModel):
    table_name: str
    incident_type: str
    severity: str
    message: str
    status: str = "open"
    detected_at: Optional[datetime] = None

class DQIncidentCreate(DQIncidentBase):
    pass

class DQIncident(DQIncidentBase):
    id: int
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)
