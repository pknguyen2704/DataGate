from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.core.trino_client import TrinoClient
from app.db.session import get_db
from app.models.user import User
from app.rbac.permissions import PermissionCode
from app.schemas.connection import (
    ConnectionCreate,
    ConnectionOut,
    ConnectionTestResult,
    ConnectionUpdate,
)
from app.schemas.table import TableOut
from app.services.connection_service import ConnectionService
from app.services.table_service import TableService


connection_router = APIRouter(prefix="/connections", tags=["Connections"])


def get_connection_service(db: Session = Depends(get_db)) -> ConnectionService:
    return ConnectionService(db)


def get_table_service(db: Session = Depends(get_db)) -> TableService:
    return TableService(db)


@connection_router.get("", response_model=list[ConnectionOut])
def list_connections(
    service: ConnectionService = Depends(get_connection_service),
    _user: User = Depends(require_permission(PermissionCode.CONNECTION_VIEW)),
):
    return service.list_connections()


@connection_router.post("", response_model=ConnectionOut, status_code=status.HTTP_201_CREATED)
def create_connection(
    body: ConnectionCreate,
    service: ConnectionService = Depends(get_connection_service),
    current_user: User = Depends(require_permission(PermissionCode.CONNECTION_CREATE)),
):
    return service.create_connection(body, current_user.id)


@connection_router.get("/{connection_id}", response_model=ConnectionOut)
def get_connection(
    connection_id: UUID,
    service: ConnectionService = Depends(get_connection_service),
    _user: User = Depends(require_permission(PermissionCode.CONNECTION_VIEW)),
):
    return service.get_connection_or_404(str(connection_id))


@connection_router.get("/{connection_id}/managed-tables", response_model=list[TableOut])
def list_managed_tables(
    connection_id: UUID,
    connection_service: ConnectionService = Depends(get_connection_service),
    table_service: TableService = Depends(get_table_service),
    _user: User = Depends(require_permission(PermissionCode.TABLE_VIEW)),
):
    connection_id_str = str(connection_id)
    connection_service.get_connection_or_404(connection_id_str)
    tables = table_service.list_tables(connection_id=connection_id_str)
    return [
        table_service.enrich_table(
            table=table,
            connection_name=table.connection.name if table.connection else None,
        )
        for table in tables
    ]


@connection_router.patch("/{connection_id}", response_model=ConnectionOut)
def update_connection(
    connection_id: UUID,
    body: ConnectionUpdate,
    service: ConnectionService = Depends(get_connection_service),
    _user: User = Depends(require_permission(PermissionCode.CONNECTION_UPDATE)),
):
    return service.update_connection(str(connection_id), body)


@connection_router.patch("/{connection_id}/deactivate", response_model=ConnectionOut)
def deactivate_connection(
    connection_id: UUID,
    service: ConnectionService = Depends(get_connection_service),
    _user: User = Depends(require_permission(PermissionCode.CONNECTION_UPDATE)),
):
    return service.deactivate_connection(str(connection_id))


@connection_router.delete("/{connection_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_connection(
    connection_id: UUID,
    service: ConnectionService = Depends(get_connection_service),
    _user: User = Depends(require_permission(PermissionCode.CONNECTION_DELETE)),
):
    service.delete_connection(str(connection_id))
    return None


@connection_router.post("/{connection_id}/test", response_model=ConnectionTestResult)
def test_connection(
    connection_id: UUID,
    service: ConnectionService = Depends(get_connection_service),
    _user: User = Depends(require_permission(PermissionCode.CONNECTION_TEST)),
):
    connection = service.get_connection_or_404(str(connection_id))
    client = TrinoClient(connection)
    try:
        client.test()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Connection test failed: {exc}",
        ) from exc
    finally:
        client.close()

    return ConnectionTestResult(success=True, message=f"Connection '{connection.name}' is reachable")


@connection_router.get("/{connection_id}/catalogs", response_model=list[str])
def list_catalogs(
    connection_id: UUID,
    service: ConnectionService = Depends(get_connection_service),
    _user: User = Depends(require_permission(PermissionCode.CONNECTION_VIEW)),
):
    connection = service.get_connection_or_404(str(connection_id))
    return [connection.iceberg_catalog_name]


@connection_router.get("/{connection_id}/schemas", response_model=list[str])
def list_schemas(
    connection_id: UUID,
    service: ConnectionService = Depends(get_connection_service),
    _user: User = Depends(require_permission(PermissionCode.CONNECTION_VIEW)),
):
    connection = service.get_connection_or_404(str(connection_id))
    client = TrinoClient(connection)
    try:
        schemas = client.list_schemas(connection.iceberg_catalog_name)
        return [
            schema
            for schema in schemas
            if schema.lower() not in {"information_schema", "pg_catalog", "sys", "system"}
        ]
    finally:
        client.close()


@connection_router.get("/{connection_id}/tables", response_model=list[str])
def list_tables(
    connection_id: UUID,
    schema: str = Query(...),
    catalog: str | None = Query(default=None),
    service: ConnectionService = Depends(get_connection_service),
    _user: User = Depends(require_permission(PermissionCode.CONNECTION_VIEW)),
):
    connection = service.get_connection_or_404(str(connection_id))
    if catalog and catalog != connection.iceberg_catalog_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Table discovery only supports the catalog configured on the connection.",
        )
    client = TrinoClient(connection)
    try:
        return client.list_tables(connection.iceberg_catalog_name, schema)
    finally:
        client.close()
