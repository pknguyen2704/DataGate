from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime, date

class DGObservabilityConfigBase(BaseModel):
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

class DGObservabilityConfigCreate(DGObservabilityConfigBase):
    pass

class DGObservabilityConfigUpdate(BaseModel):
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

class DGObservabilityConfig(DGObservabilityConfigBase):
    id: int
    last_run_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class DGObservabilityRunHistoryBase(BaseModel):
    job_id: int
    dag_id: Optional[str] = None
    dag_run_id: Optional[str] = None
    trigger_type: str = "scheduled"
    status: str = "queued"
    scheduled_for: Optional[datetime] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    error_message: Optional[str] = None

class DGObservabilityRunHistory(DGObservabilityRunHistoryBase):
    id: int
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class DGObservabilitySnapshotBase(BaseModel):
    table_name: str
    snapshot_time: datetime
    last_updated_time: Optional[datetime] = None
    total_records: Optional[int] = None
    total_size: Optional[int] = None

class DGObservabilitySnapshot(DGObservabilitySnapshotBase):
    id: int
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class DGObservabilityVolumeTSBase(BaseModel):
    table_name: str
    dt: date
    records_added: Optional[int] = 0

class DGObservabilityVolumeTS(DGObservabilityVolumeTSBase):
    id: int
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class DGObservabilityTriggerOnDemand(BaseModel):
    catalog: str
    schema_name: str
    table_name: str

class DGObservabilitySchemaBase(BaseModel):
    table_name: str
    column_name: str
    data_type: str
    snapshot_time: datetime

class DGObservabilitySchema(DGObservabilitySchemaBase):
    id: int
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class DGObservabilityIncidentBase(BaseModel):
    table_name: str
    incident_type: str
    severity: str
    message: str
    status: str = "open"
    detected_at: Optional[datetime] = None

class DGObservabilityIncidentCreate(DGObservabilityIncidentBase):
    pass

class DGObservabilityIncident(DGObservabilityIncidentBase):
    id: int
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)
