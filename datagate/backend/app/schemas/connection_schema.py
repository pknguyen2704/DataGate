from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class ConnectionBase(BaseModel):
    connection_name: str = Field(..., max_length=255)
    description: str | None = None
    trino_host: str = Field(..., max_length=255)
    trino_port: int = Field(default=8080, ge=1, le=65535)
    trino_user: str = Field(..., max_length=255)
    trino_password: str | None = None
    iceberg_rest_url: str = Field(..., max_length=255)
    iceberg_catalog_name: str = Field(..., max_length=255)
    iceberg_warehouse: str = Field(..., max_length=255)
    minio_endpoint_url: str = Field(..., max_length=255)
    minio_access_key: str = Field(..., max_length=255)
    minio_secret_key: str
    is_active: bool = True


class ConnectionCreate(ConnectionBase):
    pass


class ConnectionUpdate(BaseModel):
    connection_name: str | None = Field(default=None, max_length=255)
    description: str | None = None
    trino_host: str | None = Field(default=None, max_length=255)
    trino_port: int | None = Field(default=None, ge=1, le=65535)
    trino_user: str | None = Field(default=None, max_length=255)
    trino_password: str | None = None
    iceberg_rest_url: str | None = Field(default=None, max_length=255)
    iceberg_catalog_name: str | None = Field(default=None, max_length=255)
    iceberg_warehouse: str | None = Field(default=None, max_length=255)
    minio_endpoint_url: str | None = Field(default=None, max_length=255)
    minio_access_key: str | None = Field(default=None, max_length=255)
    minio_secret_key: str | None = None
    is_active: bool | None = None


class ConnectionOut(BaseModel):
    id: UUID
    connection_name: str
    description: str | None = None
    trino_host: str
    trino_port: int
    trino_user: str
    iceberg_rest_url: str
    iceberg_catalog_name: str
    iceberg_warehouse: str
    minio_endpoint_url: str
    is_active: bool
    created_by: UUID | None = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ConnectionLiteOut(BaseModel):
    id: UUID
    connection_name: str
    iceberg_catalog_name: str
    is_active: bool
    model_config = ConfigDict(from_attributes=True)


class ConnectionTestResult(BaseModel):
    success: bool
    message: str
