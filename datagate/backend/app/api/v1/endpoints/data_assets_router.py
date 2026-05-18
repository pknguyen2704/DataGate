from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.db.session import get_db
from app.models import User
from app.rbac.permissions import PermissionCode
from app.schemas.table_schema import (
    ProcessingHourOut,
    TableColumnOut,
    TableCreate,
    TableDetailOut,
    TableUpdate,
    TableListOut,
)
from app.services.table_service import TableService


data_assets_router = APIRouter(prefix="/data-assets", tags=["Data Assets"])


def get_table_service(db: Session = Depends(get_db)) -> TableService:
    return TableService(db)


@data_assets_router.get("/tables", response_model=TableListOut)
def list_tables(
    connection_id: str | None = Query(default=None),
    catalog_name: str | None = Query(default=None),
    schema_name: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1),
    service: TableService = Depends(get_table_service),
    _user: User = Depends(require_permission(PermissionCode.TABLE_VIEW)),
):
    # Handle empty string from frontend filters
    conn_id = connection_id if connection_id and connection_id.strip() != "" else None

    return service.list_tables(
        connection_id=conn_id,
        catalog_name=catalog_name,
        schema_name=schema_name,
        page=page,
        page_size=page_size,
    )


@data_assets_router.post(
    "/tables", response_model=TableDetailOut, status_code=status.HTTP_201_CREATED
)
def create_table(
    data: TableCreate,
    service: TableService = Depends(get_table_service),
    current_user: User = Depends(require_permission(PermissionCode.TABLE_MANAGE)),
):
    return service.create_table(data=data, owner_id=str(current_user.id))


@data_assets_router.get("/tables/{table_id}", response_model=TableDetailOut)
def get_table(
    table_id: UUID,
    service: TableService = Depends(get_table_service),
    _user: User = Depends(require_permission(PermissionCode.TABLE_VIEW)),
):
    table = service.get_table_or_404(str(table_id))
    service.validate_table_accessible(table)
    return table


@data_assets_router.put("/tables/{table_id}", response_model=TableDetailOut)
def update_table(
    table_id: UUID,
    data: TableUpdate,
    service: TableService = Depends(get_table_service),
    _user: User = Depends(require_permission(PermissionCode.TABLE_MANAGE)),
):
    return service.update_table(table_id=str(table_id), data=data)


@data_assets_router.get(
    "/tables/{table_id}/columns", response_model=list[TableColumnOut]
)
def list_table_columns(
    table_id: UUID,
    service: TableService = Depends(get_table_service),
    _user: User = Depends(require_permission(PermissionCode.TABLE_VIEW)),
):
    table = service.get_table_or_404(str(table_id))
    service.validate_table_accessible(table)
    return service.list_columns(str(table_id))


@data_assets_router.get(
    "/tables/{table_id}/processing-hours", response_model=list[ProcessingHourOut]
)
def list_table_processing_hours(
    table_id: UUID,
    service: TableService = Depends(get_table_service),
    _user: User = Depends(require_permission(PermissionCode.TABLE_VIEW)),
):
    table = service.get_table_or_404(str(table_id))
    service.validate_table_accessible(table)
    return service.list_processing_hours(str(table_id))


@data_assets_router.delete("/tables/{table_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_table(
    table_id: UUID,
    service: TableService = Depends(get_table_service),
    _user: User = Depends(require_permission(PermissionCode.TABLE_DELETE)),
):
    service.delete_table(str(table_id))
    return None
