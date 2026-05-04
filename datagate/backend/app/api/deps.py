from typing import Annotated, Callable
from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session, selectinload

from app.core.config import config
from app.core.exceptions import UnauthorizedError, ForbiddenError, NotFoundError
from app.db.session import get_db
from app.models.user import User
from app.models.role import Role
from app.models.table import Table
from app.services.auth_service import AuthService


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{config.api_v1_str}/auth/login"
)


def get_current_user(
    db: Annotated[Session, Depends(get_db)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    try:
        payload = jwt.decode(
            token,
            config.secret_key,
            algorithms=[config.algorithm],
        )
        user_id = payload.get("sub")

        if user_id is None:
            raise UnauthorizedError("Could not validate credentials")

    except JWTError:
        raise UnauthorizedError("Could not validate credentials")

    user = (
        db.query(User)
        .options(selectinload(User.roles).selectinload(Role.permissions))
        .filter(User.id == user_id)
        .first()
    )

    if user is None:
        raise UnauthorizedError("User not found")

    if not user.is_active:
        raise ForbiddenError("Account is disabled")

    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]


def require_permission(permission_code: str) -> Callable:
    def check_permission(
        db: Annotated[Session, Depends(get_db)],
        current_user: CurrentUserDep,
    ) -> User:
        auth_service = AuthService(db)
        if not auth_service.has_permission(current_user, permission_code):
            raise ForbiddenError(f"Permission required: {permission_code}")

        return current_user

    return check_permission


def check_table_access(
    table_id: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: CurrentUserDep,
) -> Table:
    table = (
        db.query(Table)
        .filter(Table.id == table_id)
        .first()
    )

    if table is None:
        raise NotFoundError("Table not found")

    if AuthService(db).is_admin(current_user):
        return table

    access = (
        db.query(UserTableAccess)
        .filter(
            UserTableAccess.user_id == current_user.id,
            UserTableAccess.table_id == table_id,
        )
        .first()
    )

    if access is None:
        raise ForbiddenError("You do not have access to this table")

    return table
