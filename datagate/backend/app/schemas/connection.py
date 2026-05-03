from datetime import datetime

from pydantic import BaseModel


class ConnectionCreate(BaseModel):
    name: str
    description: str | None = None

    trino_host: str
    trino_port: int = 8080
    trino_user: str
    trino_password: str | None = None

    iceberg_rest_url: str
    iceberg_catalog_name: str

    minio_endpoint_url: str
    minio_access_key: str
    minio_secret_key: str
    minio_region: str = "us-east-1"


class ConnectionUpdate(BaseModel):
    name: str | None = None
    description: str | None = None

    trino_host: str | None = None
    trino_port: int | None = None
    trino_user: str | None = None
    trino_password: str | None = None

    iceberg_rest_url: str | None = None
    iceberg_catalog_name: str | None = None

    minio_endpoint_url: str | None = None
    minio_access_key: str | None = None
    minio_secret_key: str | None = None
    minio_region: str | None = None

    is_active: bool | None = None


class ConnectionOut(BaseModel):
    id: str
    name: str
    description: str | None = None

    trino_host: str
    trino_port: int
    trino_user: str

    iceberg_rest_url: str
    iceberg_catalog_name: str

    minio_endpoint_url: str
    minio_access_key: str
    minio_region: str

    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class ConnectionTestResult(BaseModel):
    success: bool
    message: str


class CatalogList(BaseModel):
    catalogs: list[str]


class SchemaList(BaseModel):
    schemas: list[str]


class TableList(BaseModel):
    tables: list[str]