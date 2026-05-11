from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.connection_schema import ConnectionLiteOut


class TableBase(BaseModel):
    catalog_name: str = Field(..., max_length=255)
    schema_name: str = Field(..., max_length=255)
    table_name: str = Field(..., max_length=255)
    is_active: bool = True


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
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class TableDetailOut(TableOut):
    connection: ConnectionLiteOut | None = None


class TableLiteOut(BaseModel):
    id: UUID
    catalog_name: str
    schema_name: str
    table_name: str
    is_active: bool
    model_config = ConfigDict(from_attributes=True)


class TableColumnOut(BaseModel):
    column_name: str
    data_type: str | None = None


class ProcessingHourOut(BaseModel):
    processing_date_hour: datetime
