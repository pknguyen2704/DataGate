from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID


class BatchTableMetadataBase(BaseModel):
    table_id: UUID
    batch_added_rows: int | None = None
    batch_added_files: int | None = None
    table_total_rows: int | None = None
    table_total_files: int | None = None
    table_total_size_bytes: int | None = None
    processing_date_hour: datetime


class BatchTableMetadataCreate(BatchTableMetadataBase):
    pass


class BatchTableMetadataUpdate(BaseModel):
    batch_added_rows: int | None = None
    batch_added_files: int | None = None
    table_total_rows: int | None = None
    table_total_files: int | None = None
    table_total_size_bytes: int | None = None
    processing_date_hour: datetime | None = None


class BatchTableMetadataOut(BatchTableMetadataBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BatchTableProfilingBase(BaseModel):
    table_id: UUID
    column_name: str = Field(..., max_length=255)
    data_type: str | None = Field(default=None, max_length=100)

    completeness: float | None = None
    mean: float | None = None
    standard_deviation: float | None = None
    minimum: float | None = None
    maximum: float | None = None
    min_length: int | None = None
    max_length: int | None = None
    distinctness: float | None = None
    approx_count_distinct: int | None = None

    processing_date_hour: datetime


class BatchTableProfilingCreate(BatchTableProfilingBase):
    pass


class BatchTableProfilingUpdate(BaseModel):
    data_type: str | None = Field(default=None, max_length=100)

    completeness: float | None = None
    mean: float | None = None
    standard_deviation: float | None = None
    minimum: float | None = None
    maximum: float | None = None
    min_length: int | None = None
    max_length: int | None = None
    distinctness: float | None = None
    approx_count_distinct: int | None = None


class BatchTableProfilingOut(BatchTableProfilingBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)