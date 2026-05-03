from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_permission
from app.db.session import get_db
from app.models.user import User
from app.rbac.permissions import PermissionCode
from app.schemas.user import (
    UserCreate,
    UserOut,
    UserRoleAssign,
    UserUpdate,
)
from app.services.user_service import UserService


user_router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


def get_user_service(
    db: Session = Depends(get_db),
) -> UserService:
    return UserService(db)


@user_router.get("", response_model=list[UserOut])
def list_users(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None),
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(require_permission(PermissionCode.USER_VIEW)),
):
    return service.list_users(
        page=page,
        page_size=page_size,
        search=search,
    )


@user_router.post(
    "",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    data: UserCreate,
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(require_permission(PermissionCode.USER_CREATE)),
):
    return service.create_user(data)


@user_router.get("/me", response_model=UserOut)
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    user = service.get_user_or_404(current_user.id)
    return service.to_user_out(user)


@user_router.patch("/me", response_model=UserOut)
def update_current_user_profile(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    safe_updates = UserUpdate(
        **data.model_dump(
            exclude_unset=True,
            exclude={"is_active", "role_ids"},
        )
    )
    return service.update_user(
        user_id=current_user.id,
        data=safe_updates,
    )


@user_router.get("/{user_id}", response_model=UserOut)
def get_user(
    user_id: str,
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(require_permission(PermissionCode.USER_VIEW)),
):
    user = service.get_user_or_404(user_id)
    return service.to_user_out(user)


@user_router.patch("/{user_id}", response_model=UserOut)
def update_user(
    user_id: str,
    data: UserUpdate,
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(require_permission(PermissionCode.USER_UPDATE)),
):
    return service.update_user(
        user_id=user_id,
        data=data,
    )


@user_router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def deactivate_user(
    user_id: str,
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(require_permission(PermissionCode.USER_DELETE)),
):
    service.deactivate_user(
        user_id=user_id,
        current_user_id=current_user.id,
    )

    return None


@user_router.post("/{user_id}/roles", response_model=UserOut)
def assign_roles(
    user_id: str,
    data: UserRoleAssign,
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(require_permission(PermissionCode.USER_UPDATE)),
):
    return service.assign_roles(
        user_id=user_id,
        data=data,
    )
