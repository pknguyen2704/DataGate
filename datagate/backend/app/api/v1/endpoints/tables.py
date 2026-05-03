from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import check_table_access, require_permission
from app.db.session import get_db
from app.models.user import User
from app.models.table import Table
from app.rbac.permissions import PermissionCode
from app.schemas.table import (
    TableAccessGrant,
    TableCreate,
    TableOut,
    TableOverviewOut,
    TableUpdate,
)
from app.services.table_service import TableService


table_router = APIRouter(
    prefix="/tables",
    tags=["Tables"],
)


def get_table_service(
    db: Session = Depends(get_db),
) -> TableService:
    return TableService(db)


@table_router.get("", response_model=list[TableOut])
def list_tables(
    connection_id: UUID | None = Query(default=None),
    service: TableService = Depends(get_table_service),
    current_user: User = Depends(require_permission(PermissionCode.TABLE_VIEW)),
):
    tables = service.list_tables(connection_id=str(connection_id) if connection_id else None)

    return [
        service.enrich_table(
            table=table,
            connection_name=table.connection.name if table.connection else None,
        )
        for table in tables
    ]


@table_router.post(
    "",
    response_model=TableOut,
    status_code=status.HTTP_201_CREATED,
)
def create_table(
    data: TableCreate,
    service: TableService = Depends(get_table_service),
    current_user: User = Depends(require_permission(PermissionCode.TABLE_CREATE)),
):
    table = service.create_table(
        data=data,
        owner_id=current_user.id,
    )

    return service.enrich_table(
        table=table,
        connection_name=table.connection.name if table.connection else None,
    )


@table_router.get("/{table_id}", response_model=TableOut)
def get_table(
    table: Table = Depends(check_table_access),
    service: TableService = Depends(get_table_service),
):
    return service.enrich_table(
        table=table,
        connection_name=table.connection.name if table.connection else None,
    )


@table_router.patch("/{table_id}", response_model=TableOut)
def update_table(
    table_id: str,
    data: TableUpdate,
    service: TableService = Depends(get_table_service),
    current_user: User = Depends(require_permission(PermissionCode.TABLE_UPDATE)),
):
    table = service.update_table(
        table_id=table_id,
        data=data,
    )

    return service.enrich_table(
        table=table,
        connection_name=table.connection.name if table.connection else None,
    )


@table_router.delete(
    "/{table_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_table(
    table_id: str,
    service: TableService = Depends(get_table_service),
    current_user: User = Depends(require_permission(PermissionCode.TABLE_DELETE)),
):
    service.delete_table(table_id)
    return None


@table_router.patch("/{table_id}/deactivate", response_model=TableOut)
def deactivate_table(
    table_id: str,
    service: TableService = Depends(get_table_service),
    current_user: User = Depends(require_permission(PermissionCode.TABLE_UPDATE)),
):
    table = service.deactivate_table(table_id)

    return service.enrich_table(
        table=table,
        connection_name=table.connection.name if table.connection else None,
    )


@table_router.get("/{table_id}/overview", response_model=TableOverviewOut)
def get_table_overview(
    table: Table = Depends(check_table_access),
    service: TableService = Depends(get_table_service),
):
    return service.get_table_overview(table.id)


@table_router.post("/{table_id}/accesses", status_code=status.HTTP_201_CREATED)
def grant_table_access(
    table_id: str,
    data: TableAccessGrant,
    service: TableService = Depends(get_table_service),
    current_user: User = Depends(require_permission(PermissionCode.TABLE_GRANT_ACCESS)),
):
    service.grant_table_access(
        table_id=table_id,
        user_id=data.user_id,
        granted_by=current_user.id,
    )

    return {
        "message": "Table access granted successfully"
    }


@table_router.delete(
    "/{table_id}/accesses/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def revoke_table_access(
    table_id: str,
    user_id: str,
    service: TableService = Depends(get_table_service),
    current_user: User = Depends(require_permission(PermissionCode.TABLE_REVOKE_ACCESS)),
):
    service.revoke_table_access(
        table_id=table_id,
        user_id=user_id,
    )

    return None
