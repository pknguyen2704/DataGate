from datetime import datetime
from pydantic import BaseModel


class ManagedTableNodeOut(BaseModel):
    table_id: str
    table_name: str


class ConnectionVarOut(BaseModel):
    id: str
    name: str


class ManagedSchemaNodeOut(BaseModel):
    schema_name: str
    tables: list[ManagedTableNodeOut]


class ObservabilityVariablesOut(BaseModel):
    catalogs: list[str]
    schemas: list[str]
    tables: list[str]
    connections: list[ConnectionVarOut] = []
    processing_date_hours: list[datetime]


class ObservabilityEmbedUrlOut(BaseModel):
    url: str


class TimeRangeOut(BaseModel):
    default_from: datetime | None
    default_to: datetime | None
