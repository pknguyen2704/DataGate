from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.connection_schema import ConnectionLiteOut
from app.schemas.common_schema import PaginatedResponse


class TableBase(BaseModel):
    catalog_name: str = Field(..., max_length=255)
    schema_name: str = Field(..., max_length=255)
    table_name: str = Field(..., max_length=255)


class TableCreate(TableBase):
    connection_id: UUID


class TableUpdate(BaseModel):
    connection_id: UUID | None = None
    catalog_name: str | None = Field(default=None, max_length=255)
    schema_name: str | None = Field(default=None, max_length=255)
    table_name: str | None = Field(default=None, max_length=255)
    is_active: bool | None = None


class TableOut(TableBase):
    id: UUID
    connection_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    latest_processing_date_hour: datetime | None = None
    has_anomaly_config: bool = False
    model_config = ConfigDict(from_attributes=True)


class TableDetailOut(TableOut):
    connection: ConnectionLiteOut | None = None


class TableLiteOut(BaseModel):
    id: UUID
    catalog_name: str
    schema_name: str
    table_name: str
    is_active: bool | None = None
    latest_processing_date_hour: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


class TableListOut(PaginatedResponse[TableOut]):
    pass


class TableColumnOut(BaseModel):
    column_name: str
    data_type: str | None = None


class ProcessingHourOut(BaseModel):
    processing_date_hour: datetime
