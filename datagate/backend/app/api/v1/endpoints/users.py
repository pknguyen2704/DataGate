"""
User management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid
from datetime import datetime

from app.db.session import get_db
from app.models.auth import User, Role
from app.core.security import get_password_hash
from app.core.permissions import PermissionCode
from app.api.deps import get_current_user, require_permission

router = APIRouter()


# ── Schemas ──────────────────────────────────────────────────────────────────

class UserOut(BaseModel):
    id: str
    username: str
    email: str
    full_name: Optional[str]
    is_active: bool
    roles: list[str]
    permissions: list[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role_ids: list[str] = []


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


class PaginatedUsers(BaseModel):
    items: list[UserOut]
    total: int
    page: int
    page_size: int


# ── Helpers ──────────────────────────────────────────────────────────────────

def _user_to_out(user: User) -> UserOut:
    return UserOut(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        roles=[r.name for r in user.roles if r.is_active],
        permissions=list(user.permission_codes),
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.get("", response_model=PaginatedUsers)
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(PermissionCode.USER_VIEW)),
):
    """List all users with pagination and search."""
    query = select(User).options(selectinload(User.roles))

    if search:
        query = query.where(
            or_(
                User.username.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                User.full_name.ilike(f"%{search}%"),
            )
        )

    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar()

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    users = result.scalars().all()

    return PaginatedUsers(
        items=[_user_to_out(u) for u in users],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(
    body: UserCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(PermissionCode.USER_CREATE)),
):
    # Check uniqueness
    result = await db.execute(
        select(User).where(or_(User.username == body.username, User.email == body.email))
    )
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Username or email already registered")

    user = User(
        id=str(uuid.uuid4()),
        username=body.username,
        email=body.email,
        hashed_password=get_password_hash(body.password),
        full_name=body.full_name,
    )
    db.add(user)
    await db.flush()

    if body.role_ids:
        roles_result = await db.execute(select(Role).where(Role.id.in_(body.role_ids)))
        roles = roles_result.scalars().all()
        user.roles.extend(roles)

    await db.flush()
    await db.refresh(user)
    return _user_to_out(user)


@router.get("/{user_id}", response_model=UserOut)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(PermissionCode.USER_VIEW)),
):
    result = await db.execute(
        select(User).options(selectinload(User.roles)).where(User.id == user_id)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return _user_to_out(user)


@router.patch("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: str,
    body: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(PermissionCode.USER_UPDATE)),
):
    result = await db.execute(
        select(User).options(selectinload(User.roles)).where(User.id == user_id)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if body.full_name is not None:
        user.full_name = body.full_name
    if body.email is not None:
        user.email = body.email
    if body.password is not None:
        user.hashed_password = get_password_hash(body.password)
    if body.is_active is not None:
        user.is_active = body.is_active

    await db.flush()
    await db.refresh(user)
    return _user_to_out(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(PermissionCode.USER_DELETE)),
):
    """Soft-delete: set is_active = False."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot deactivate your own account")
    user.is_active = False


@router.post("/{user_id}/roles", response_model=UserOut)
async def assign_roles(
    user_id: str,
    role_ids: list[str],
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(PermissionCode.ROLE_ASSIGN_PERMISSION)),
):
    result = await db.execute(
        select(User).options(selectinload(User.roles)).where(User.id == user_id)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    roles_result = await db.execute(select(Role).where(Role.id.in_(role_ids)))
    roles = roles_result.scalars().all()
    user.roles = roles
    await db.flush()
    await db.refresh(user)
    return _user_to_out(user)
