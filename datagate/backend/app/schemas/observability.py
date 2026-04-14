from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime, date

class DQJobConfigBase(BaseModel):
    catalog: str
    schema_name: str
    table_name: str
    hour: int
    minute: int
    job_type: str = "observability"
    is_active: bool = True

class DQJobConfigCreate(DQJobConfigBase):
    pass

class DQJobConfig(DQJobConfigBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class DQTableSnapshotBase(BaseModel):
    table_name: str
    snapshot_time: datetime
    last_updated_time: datetime
    total_records: int
    total_size: int

class DQTableSnapshot(DQTableSnapshotBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class DQTableVolumeTSBase(BaseModel):
    table_name: str
    dt: date
    records_added: Optional[int] = 0

class DQTableVolumeTS(DQTableVolumeTSBase):
    id: int
    created_at: datetime
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
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class DQColumnStatsBase(BaseModel):
    table_name: str
    column_name: str
    nulls: int
    total: int
    snapshot_time: datetime

class DQColumnStats(DQColumnStatsBase):
    id: int
    created_at: datetime
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
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
