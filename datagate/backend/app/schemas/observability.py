from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class ObservabilityConfigBase(BaseModel):
    catalog: str
    schema_name: str
    table_name: str
    is_active: bool = True

class ObservabilityConfigCreate(ObservabilityConfigBase):
    pass

class ObservabilityConfig(ObservabilityConfigBase):
    id: int
    last_run_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class ObservabilitySnapshotBase(BaseModel):
    table_name: str
    schema_name: str
    catalog: str
    snapshot_time: datetime
    last_updated_time: Optional[datetime] = None
    total_records: Optional[int] = None
    total_size: Optional[int] = None

class ObservabilitySnapshot(ObservabilitySnapshotBase):
    id: int
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class ObservabilityVolumeTSBase(BaseModel):
    table_name: str
    schema_name: str
    catalog: str
    dt: datetime
    records_added: Optional[int] = 0

class ObservabilityVolumeTS(ObservabilityVolumeTSBase):
    id: int
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class ObservabilityTriggerOnDemand(BaseModel):
    catalog: str
    schema_name: str
    table_name: str

class ObservabilitySchemaBase(BaseModel):
    table_name: str
    schema_name: str
    catalog: str
    column_name: str
    data_type: str
    snapshot_time: datetime

class ObservabilitySchema(ObservabilitySchemaBase):
    id: int
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class ObservabilityIncidentBase(BaseModel):
    table_name: str
    schema_name: str
    catalog: str
    incident_type: str
    severity: str
    message: str
    status: str = "open"
    detected_at: Optional[datetime] = None

class ObservabilityIncidentCreate(ObservabilityIncidentBase):
    pass

class ObservabilityIncident(ObservabilityIncidentBase):
    id: int
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)
