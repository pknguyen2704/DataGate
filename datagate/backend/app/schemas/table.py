from datetime import datetime

from pydantic import BaseModel


class TableCreate(BaseModel):
    connection_id: str
    catalog_name: str
    schema_name: str
    table_name: str
    owner_user_id: str | None = None


TableAdd = TableCreate


class TableUpdate(BaseModel):
    owner_user_id: str | None = None
    is_active: bool | None = None


class TableOut(BaseModel):
    id: str
    connection_id: str
    connection_name: str | None = None

    catalog_name: str
    schema_name: str
    table_name: str

    owner_user_id: str | None = None
    is_active: bool

    created_at: datetime
    updated_at: datetime

    latest_date_hour: datetime | None = None
    latest_record_count: int | None = None

    model_config = {
        "from_attributes": True
    }


class TableAccessGrant(BaseModel):
    user_id: str


class PaginatedTables(BaseModel):
    items: list[TableOut]
    total: int
    page: int
    page_size: int


class ExploreTableItem(BaseModel):
    id: str
    connection_id: str
    catalog_name: str
    schema_name: str
    table_name: str
    full_name: str
    is_active: bool


class ExploreConnectionItem(BaseModel):
    connection_id: str
    connection_name: str
    schemas: list[str]
    tables: list[ExploreTableItem]


class TableOverviewOut(BaseModel):
    id: str
    connection_id: str
    connection_name: str | None = None

    catalog_name: str
    schema_name: str
    table_name: str
    full_name: str

    owner_user_id: str | None = None
    is_active: bool

    latest_date_hour: datetime | None = None
    latest_record_count: int | None = None
    latest_file_count: int | None = None
    latest_size_bytes: int | None = None
