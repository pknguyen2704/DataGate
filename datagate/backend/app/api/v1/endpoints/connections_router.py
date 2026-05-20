from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.db.session import get_db
from app.models import User
from app.rbac.permissions import PermissionCode
from app.schemas.connection_schema import (
    ConnectionCreate,
    ConnectionListOut,
    ConnectionOut,
    ConnectionTestResult,
    ConnectionUpdate,
)
from app.services.connection_service import ConnectionService


connections_router = APIRouter(prefix="/connections", tags=["Connections"])


def get_connection_service(db: Session = Depends(get_db)) -> ConnectionService:
    return ConnectionService(db)


@connections_router.get("", response_model=ConnectionListOut)
def list_connections(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    is_active: bool | None = Query(default=None),
    service: ConnectionService = Depends(get_connection_service),
    _user: User = Depends(require_permission(PermissionCode.CONNECTION_MANAGE)),
):
    return service.list_connections(page=page, page_size=page_size, is_active=is_active)


@connections_router.post(
    "", response_model=ConnectionOut, status_code=status.HTTP_201_CREATED
)
def create_connection(
    body: ConnectionCreate,
    service: ConnectionService = Depends(get_connection_service),
    current_user: User = Depends(require_permission(PermissionCode.CONNECTION_MANAGE)),
):
    return service.create_connection(body, str(current_user.id))


@connections_router.get("/{connection_id}", response_model=ConnectionOut)
def get_connection(
    connection_id: UUID,
    service: ConnectionService = Depends(get_connection_service),
    _user: User = Depends(require_permission(PermissionCode.CONNECTION_MANAGE)),
):
    return service.get_connection_or_404(str(connection_id))


@connections_router.patch("/{connection_id}", response_model=ConnectionOut)
def update_connection(
    connection_id: UUID,
    body: ConnectionUpdate,
    service: ConnectionService = Depends(get_connection_service),
    current_user: User = Depends(require_permission(PermissionCode.CONNECTION_MANAGE)),
):
    return service.update_connection(str(connection_id), body, str(current_user.id))


@connections_router.post("/{connection_id}/test", response_model=ConnectionTestResult)
def test_connection(
    connection_id: UUID,
    service: ConnectionService = Depends(get_connection_service),
    _user: User = Depends(require_permission(PermissionCode.CONNECTION_MANAGE)),
):
    return service.test_connection(str(connection_id))


@connections_router.post("/{connection_id}/deactivate", response_model=ConnectionOut)
def deactivate_connection(
    connection_id: UUID,
    service: ConnectionService = Depends(get_connection_service),
    _user: User = Depends(require_permission(PermissionCode.CONNECTION_MANAGE)),
):
    return service.deactivate_connection(str(connection_id))


@connections_router.post("/{connection_id}/activate", response_model=ConnectionOut)
def activate_connection(
    connection_id: UUID,
    service: ConnectionService = Depends(get_connection_service),
    _user: User = Depends(require_permission(PermissionCode.CONNECTION_MANAGE)),
):
    return service.activate_connection(str(connection_id))


@connections_router.get("/{connection_id}/discover-tables")
def discover_tables(
    connection_id: UUID,
    schema: str | None = Query(default=None),
    service: ConnectionService = Depends(get_connection_service),
    _user: User = Depends(require_permission(PermissionCode.CONNECTION_MANAGE)),
):
    if not schema:
        return service.list_schemas(str(connection_id))
    return service.list_tables(str(connection_id), schema=schema)


@connections_router.post("/{connection_id}/managed-tables")
def add_managed_table(
    connection_id: UUID,
    catalog: str,
    schema: str,
    table_name: str,
    service: ConnectionService = Depends(get_connection_service),
    _user: User = Depends(require_permission(PermissionCode.CONNECTION_MANAGE)),
):
    # This logic should be in ConnectionService, I'll add it there.
    return service.add_managed_table(str(connection_id), catalog, schema, table_name)


@connections_router.delete(
    "/{connection_id}/managed-tables/{table_id}", status_code=status.HTTP_204_NO_CONTENT
)
def remove_managed_table(
    connection_id: UUID,
    table_id: UUID,
    service: ConnectionService = Depends(get_connection_service),
    _user: User = Depends(require_permission(PermissionCode.CONNECTION_MANAGE)),
):
    service.remove_managed_table(str(table_id))
    return None
