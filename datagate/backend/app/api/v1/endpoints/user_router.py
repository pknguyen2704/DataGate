from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_permission
from app.db.session import get_db
from app.models import User
from app.rbac.permissions import PermissionCode
from app.schemas.user import UserCreate, UserListOut, UserOut, UserProfileUpdate, UserRoleAssign, UserUpdate
from app.services.user_service import UserService


user_router = APIRouter(prefix="/users", tags=["Users"])


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)


@user_router.get("", response_model=UserListOut)
def list_users(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None),
    service: UserService = Depends(get_user_service),
    _user: User = Depends(require_permission(PermissionCode.USER_VIEW)),
):
    return service.list_users(page=page, page_size=page_size, search=search)


@user_router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    data: UserCreate,
    service: UserService = Depends(get_user_service),
    _user: User = Depends(require_permission(PermissionCode.USER_CREATE)),
):
    return service.create_user(data)


@user_router.get("/me", response_model=UserOut)
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    return service.to_user_out(service.get_user_or_404(str(current_user.id)))


@user_router.patch("/me", response_model=UserOut)
def update_current_user_profile(
    data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    return service.update_user(user_id=str(current_user.id), data=data)


@user_router.get("/{user_id}", response_model=UserOut)
def get_user(
    user_id: UUID,
    service: UserService = Depends(get_user_service),
    _user: User = Depends(require_permission(PermissionCode.USER_VIEW)),
):
    return service.to_user_out(service.get_user_or_404(str(user_id)))


@user_router.patch("/{user_id}", response_model=UserOut)
def update_user(
    user_id: UUID,
    data: UserUpdate,
    service: UserService = Depends(get_user_service),
    _user: User = Depends(require_permission(PermissionCode.USER_UPDATE)),
):
    return service.update_user(user_id=str(user_id), data=data)


@user_router.patch("/{user_id}/activate", response_model=UserOut)
def activate_user(
    user_id: UUID,
    service: UserService = Depends(get_user_service),
    _user: User = Depends(require_permission(PermissionCode.USER_UPDATE)),
):
    return service.activate_user(str(user_id))


@user_router.patch("/{user_id}/deactivate", response_model=UserOut)
def deactivate_user(
    user_id: UUID,
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(require_permission(PermissionCode.USER_DELETE)),
):
    return service.deactivate_user(user_id=str(user_id), current_user_id=str(current_user.id))


@user_router.put("/{user_id}/roles", response_model=UserOut)
def assign_roles(
    user_id: UUID,
    data: UserRoleAssign,
    service: UserService = Depends(get_user_service),
    _user: User = Depends(require_permission(PermissionCode.USER_UPDATE)),
):
    return service.assign_roles(user_id=str(user_id), data=data)