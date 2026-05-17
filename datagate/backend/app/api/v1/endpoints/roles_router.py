from typing import Annotated
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.db.session import get_db
from app.models import User
from app.rbac.permissions import PermissionCode
from app.schemas.role_schema import (
    PermissionAssign,
    RoleCreate,
    RoleOut,
    RoleUpdate,
    RoleListOut,
)
from app.services.role_service import RoleService


roles_router = APIRouter(tags=["Roles"])


def get_role_service(
    db: Annotated[Session, Depends(get_db)],
) -> RoleService:
    return RoleService(db)


RoleServiceDep = Annotated[RoleService, Depends(get_role_service)]


@roles_router.get("", response_model=RoleListOut)
def list_roles(
    service: RoleServiceDep,
    _user: Annotated[User, Depends(require_permission(PermissionCode.USER_MANAGE))],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
):
    return service.list_roles(page=page, page_size=page_size)


@roles_router.post(
    "",
    response_model=RoleOut,
    status_code=status.HTTP_201_CREATED,
)
def create_role(
    data: RoleCreate,
    service: RoleServiceDep,
    _user: Annotated[User, Depends(require_permission(PermissionCode.USER_MANAGE))],
):
    return service.create_role(data)


@roles_router.get("/{role_id}", response_model=RoleOut)
def get_role(
    role_id: str,
    service: RoleServiceDep,
    _user: Annotated[User, Depends(require_permission(PermissionCode.USER_MANAGE))],
):
    return service.get_role_or_404(role_id)


@roles_router.patch("/{role_id}", response_model=RoleOut)
def update_role(
    role_id: str,
    data: RoleUpdate,
    service: RoleServiceDep,
    _user: Annotated[User, Depends(require_permission(PermissionCode.USER_MANAGE))],
):
    return service.update_role(
        role_id=role_id,
        data=data,
    )


@roles_router.delete(
    "/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_role(
    role_id: str,
    service: RoleServiceDep,
    _user: Annotated[User, Depends(require_permission(PermissionCode.USER_MANAGE))],
):
    service.delete_role(role_id)
    return None


@roles_router.patch("/{role_id}/permissions", response_model=RoleOut)
def assign_permissions(
    role_id: str,
    data: PermissionAssign,
    service: RoleServiceDep,
    _user: Annotated[User, Depends(require_permission(PermissionCode.USER_MANAGE))],
):
    return service.assign_permissions_to_role(
        role_id=role_id,
        permission_ids=data.permission_ids,
    )
