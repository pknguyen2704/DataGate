from typing import Annotated
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.db.session import get_db
from app.models import User
from app.rbac.permissions import PermissionCode
from app.schemas.role_schema import RoleListOut, RoleOut
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


@roles_router.get("/{role_id}", response_model=RoleOut)
def get_role(
    role_id: str,
    service: RoleServiceDep,
    _user: Annotated[User, Depends(require_permission(PermissionCode.USER_MANAGE))],
):
    return service.get_role_or_404(role_id)
