from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.db.session import get_db
from app.models import User
from app.rbac.permissions import PermissionCode
from app.schemas.user_schema import (
    UserCreate,
    UserListOut,
    UserOut,
    UserUpdate,
)
from app.services.user_service import UserService


users_router = APIRouter(tags=["Users"])


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)


@users_router.get("", response_model=UserListOut)
def list_users(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None),
    service: UserService = Depends(get_user_service),
    _user: User = Depends(require_permission(PermissionCode.USER_MANAGE)),
):
    return service.list_users(page=page, page_size=page_size, search=search)


@users_router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    data: UserCreate,
    service: UserService = Depends(get_user_service),
    _user: User = Depends(require_permission(PermissionCode.USER_MANAGE)),
):
    return service.create_user(data)


@users_router.get("/{user_id}", response_model=UserOut)
def get_user(
    user_id: UUID,
    service: UserService = Depends(get_user_service),
    _user: User = Depends(require_permission(PermissionCode.USER_MANAGE)),
):
    return service.to_user_out(service.get_user_or_404(str(user_id)))


@users_router.patch("/{user_id}", response_model=UserOut)
def update_user(
    user_id: UUID,
    data: UserUpdate,
    service: UserService = Depends(get_user_service),
    _user: User = Depends(require_permission(PermissionCode.USER_MANAGE)),
):
    return service.update_user(user_id=str(user_id), data=data)


@users_router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: UUID,
    service: UserService = Depends(get_user_service),
    _user: User = Depends(require_permission(PermissionCode.USER_MANAGE)),
):
    service.delete_user(str(user_id))

