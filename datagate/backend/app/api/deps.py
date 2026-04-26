"""
API Dependencies — get_db, get_current_user, require_permission, check_table_access
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.core.config import settings
from app.models.auth import User
from app.models.connection import TableInfo, UserTableAccess

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> User:
    """Decode JWT and return the current user."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise CREDENTIALS_EXCEPTION
    except JWTError:
        raise CREDENTIALS_EXCEPTION

    result = await db.execute(
        select(User)
        .options(selectinload(User.roles))
        .where(User.id == user_id)
    )
    user = result.scalars().first()

    if user is None:
        raise CREDENTIALS_EXCEPTION
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled")

    return user


def require_permission(permission_code: str):
    """Dependency factory: requires the current user to have a specific permission."""
    async def _check(current_user: User = Depends(get_current_user)):
        if not current_user.has_permission(permission_code):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission required: {permission_code}",
            )
        return current_user
    return _check


async def check_table_access(
    table_id: str,
    access_level: str = "view",  # "view" or "manage"
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TableInfo:
    """
    Check if current user can access a table.
    Admins (users with table:grant_access permission) bypass this check.
    """
    from app.core.permissions import PermissionCode

    # Load table
    result = await db.execute(select(TableInfo).where(TableInfo.id == table_id))
    table = result.scalars().first()
    if not table:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")

    # Admins bypass table-level access check
    if current_user.has_permission(PermissionCode.TABLE_GRANT_ACCESS):
        return table

    # Check user_table_access
    access_result = await db.execute(
        select(UserTableAccess).where(
            UserTableAccess.user_id == current_user.id,
            UserTableAccess.table_id == table_id,
        )
    )
    access = access_result.scalars().first()

    if not access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this table",
        )

    if access_level == "manage" and access.access_level == "view":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You need manage-level access for this action",
        )

    return table
