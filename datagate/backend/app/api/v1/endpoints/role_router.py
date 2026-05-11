from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.db.session import get_db
from app.models import User
from app.rbac.permissions import PermissionCode
from app.schemas.permission_schema import PermissionOut
from app.schemas.role_schema import PermissionAssign, RoleCreate, RoleOut, RoleUpdate
from app.services.role_service import RoleService


role_router = APIRouter(
    prefix="/roles",
    tags=["Roles"],
)


def get_role_service(
    db: Annotated[Session, Depends(get_db)],
) -> RoleService:
    return RoleService(db)


RoleServiceDep = Annotated[RoleService, Depends(get_role_service)]
CurrentUserDep = Annotated[User, Depends(require_permission(PermissionCode.ROLE_VIEW))]


@role_router.get("/permissions", response_model=list[PermissionOut])
def list_permissions(
    service: RoleServiceDep,
    current_user: CurrentUserDep,
):
    return service.list_permissions()


@role_router.get("", response_model=list[RoleOut])
def list_roles(
    service: RoleServiceDep,
    current_user: CurrentUserDep,
):
    return service.list_roles()


@role_router.post(
    "",
    response_model=RoleOut,
    status_code=status.HTTP_201_CREATED,
)
def create_role(
    data: RoleCreate,
    service: RoleServiceDep,
    current_user: Annotated[User, Depends(require_permission(PermissionCode.ROLE_CREATE))],
):
    return service.create_role(data)


@role_router.get("/{role_id}", response_model=RoleOut)
def get_role(
    role_id: str,
    service: RoleServiceDep,
    current_user: CurrentUserDep,
):
    return service.get_role_or_404(role_id)


@role_router.patch("/{role_id}", response_model=RoleOut)
def update_role(
    role_id: str,
    data: RoleUpdate,
    service: RoleServiceDep,
    current_user: Annotated[User, Depends(require_permission(PermissionCode.ROLE_UPDATE))],
):
    return service.update_role(
        role_id=role_id,
        data=data,
    )


@role_router.delete(
    "/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_role(
    role_id: str,
    service: RoleServiceDep,
    current_user: Annotated[User, Depends(require_permission(PermissionCode.ROLE_DELETE))],
):
    service.delete_role(role_id)
    return None


@role_router.post("/{role_id}/permissions", response_model=RoleOut)
def assign_permissions(
    role_id: str,
    data: PermissionAssign,
    service: RoleServiceDep,
    current_user: Annotated[User, Depends(require_permission(PermissionCode.ROLE_ASSIGN_PERMISSION))],
):
    return service.assign_permissions_to_role(
        role_id=role_id,
        permission_ids=data.permission_ids,
    )
