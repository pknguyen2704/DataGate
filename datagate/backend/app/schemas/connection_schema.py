from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.common_schema import PaginatedResponse


class ConnectionBase(BaseModel):
    connection_name: str = Field(..., max_length=255)
    description: str | None = None
    query_engine_host: str = Field(..., max_length=255)
    query_engine_port: int = Field(default=8080, ge=1, le=65535)
    query_engine_user: str = Field(..., max_length=255)
    query_engine_password: str | None = None
    rest_url: str = Field(..., max_length=255)
    catalog_name: str = Field(..., max_length=255)
    catalog_warehouse: str = Field(..., max_length=255)
    storage_endpoint_url: str = Field(..., max_length=255)
    storage_access_key: str = Field(..., max_length=255)
    storage_secret_key: str
    is_active: bool = True


class ConnectionCreate(ConnectionBase):
    pass


class ConnectionUpdate(BaseModel):
    connection_name: str | None = Field(default=None, max_length=255)
    description: str | None = None
    query_engine_host: str | None = Field(default=None, max_length=255)
    query_engine_port: int | None = Field(default=None, ge=1, le=65535)
    query_engine_user: str | None = Field(default=None, max_length=255)
    query_engine_password: str | None = None
    rest_url: str | None = Field(default=None, max_length=255)
    catalog_name: str | None = Field(default=None, max_length=255)
    catalog_warehouse: str | None = Field(default=None, max_length=255)
    storage_endpoint_url: str | None = Field(default=None, max_length=255)
    storage_access_key: str | None = Field(default=None, max_length=255)
    storage_secret_key: str | None = None
    is_active: bool | None = None


class ConnectionOut(BaseModel):
    id: UUID
    connection_name: str
    description: str | None = None
    query_engine_host: str
    query_engine_port: int
    query_engine_user: str
    rest_url: str
    catalog_name: str
    catalog_warehouse: str
    storage_endpoint_url: str
    storage_access_key: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ConnectionLiteOut(BaseModel):
    id: UUID
    connection_name: str
    catalog_name: str
    is_active: bool
    model_config = ConfigDict(from_attributes=True)


class ConnectionListOut(PaginatedResponse[ConnectionOut]):
    pass

