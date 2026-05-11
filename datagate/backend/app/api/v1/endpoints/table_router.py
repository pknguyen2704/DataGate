from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.db.session import get_db
from app.models import User
from app.rbac.permissions import PermissionCode
from app.schemas.table_schema import ProcessingHourOut, TableColumnOut, TableCreate, TableDetailOut, TableUpdate
from app.services.table_service import TableService


table_router = APIRouter(prefix="/tables", tags=["Tables"])


def get_table_service(db: Session = Depends(get_db)) -> TableService:
    return TableService(db)


@table_router.get("", response_model=list[TableDetailOut])
def list_tables(
    connection_id: UUID | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    service: TableService = Depends(get_table_service),
    _user: User = Depends(require_permission(PermissionCode.TABLE_VIEW)),
):
    return service.list_tables(
        connection_id=str(connection_id) if connection_id else None,
        is_active=is_active,
    )


@table_router.post("", response_model=TableDetailOut, status_code=status.HTTP_201_CREATED)
def create_table(
    data: TableCreate,
    service: TableService = Depends(get_table_service),
    current_user: User = Depends(require_permission(PermissionCode.TABLE_CREATE)),
):
    return service.create_table(data=data, owner_id=str(current_user.id))


@table_router.get("/{table_id}", response_model=TableDetailOut)
def get_table(
    table_id: UUID,
    service: TableService = Depends(get_table_service),
    _user: User = Depends(require_permission(PermissionCode.TABLE_VIEW)),
):
    return service.get_table_or_404(str(table_id))


@table_router.put("/{table_id}", response_model=TableDetailOut)
def update_table(
    table_id: UUID,
    data: TableUpdate,
    service: TableService = Depends(get_table_service),
    _user: User = Depends(require_permission(PermissionCode.TABLE_UPDATE)),
):
    return service.update_table(table_id=str(table_id), data=data)


@table_router.get("/{table_id}/columns", response_model=list[TableColumnOut])
def list_table_columns(
    table_id: UUID,
    service: TableService = Depends(get_table_service),
    _user: User = Depends(require_permission(PermissionCode.TABLE_VIEW)),
):
    return service.list_columns(str(table_id))


@table_router.get("/{table_id}/processing-hours", response_model=list[ProcessingHourOut])
def list_table_processing_hours(
    table_id: UUID,
    service: TableService = Depends(get_table_service),
    _user: User = Depends(require_permission(PermissionCode.TABLE_VIEW)),
):
    return service.list_processing_hours(str(table_id))


@table_router.patch("/{table_id}/activate", response_model=TableDetailOut)
def activate_table(
    table_id: UUID,
    service: TableService = Depends(get_table_service),
    _user: User = Depends(require_permission(PermissionCode.TABLE_UPDATE)),
):
    return service.activate_table(str(table_id))


@table_router.patch("/{table_id}/deactivate", response_model=TableDetailOut)
def deactivate_table(
    table_id: UUID,
    service: TableService = Depends(get_table_service),
    _user: User = Depends(require_permission(PermissionCode.TABLE_UPDATE)),
):
    return service.deactivate_table(str(table_id))


@table_router.delete("/{table_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_table(
    table_id: UUID,
    service: TableService = Depends(get_table_service),
    _user: User = Depends(require_permission(PermissionCode.TABLE_DELETE)),
):
    service.delete_table(str(table_id))
    return None
