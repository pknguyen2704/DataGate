"""
Roles & Permissions endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime

from app.db.session import get_db
from app.models.auth import User, Role, Permission
from app.core.permissions import PermissionCode, ALL_PERMISSIONS
from app.api.deps import get_current_user, require_permission

router = APIRouter()


# ── Schemas ──────────────────────────────────────────────────────────────────

class PermissionOut(BaseModel):
    id: str
    code: str
    name: str
    group: Optional[str]


class RoleOut(BaseModel):
    id: str
    name: str
    description: Optional[str]
    is_active: bool
    is_system: bool
    permissions: list[PermissionOut]
    created_at: datetime


class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


# ── Permissions ───────────────────────────────────────────────────────────────

@router.get("/permissions", response_model=list[PermissionOut])
async def list_permissions(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(PermissionCode.ROLE_VIEW)),
):
    """Return all permission codes defined in the system."""
    result = await db.execute(select(Permission))
    perms = result.scalars().all()
    return [PermissionOut(id=p.id, code=p.code, name=p.name, group=p.group) for p in perms]


# ── Roles ────────────────────────────────────────────────────────────────────

@router.get("", response_model=list[RoleOut])
async def list_roles(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(PermissionCode.ROLE_VIEW)),
):
    result = await db.execute(
        select(Role).options(selectinload(Role.permissions))
    )
    roles = result.scalars().all()
    return [_role_to_out(r) for r in roles]


@router.post("", response_model=RoleOut, status_code=status.HTTP_201_CREATED)
async def create_role(
    body: RoleCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(PermissionCode.ROLE_CREATE)),
):
    result = await db.execute(select(Role).where(Role.name == body.name))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Role name already exists")

    role = Role(id=str(uuid.uuid4()), name=body.name, description=body.description)
    db.add(role)
    await db.flush()
    await db.refresh(role)
    return _role_to_out(role)


@router.get("/{role_id}", response_model=RoleOut)
async def get_role(
    role_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(PermissionCode.ROLE_VIEW)),
):
    result = await db.execute(
        select(Role).options(selectinload(Role.permissions)).where(Role.id == role_id)
    )
    role = result.scalars().first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return _role_to_out(role)


@router.patch("/{role_id}", response_model=RoleOut)
async def update_role(
    role_id: str,
    body: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(PermissionCode.ROLE_UPDATE)),
):
    result = await db.execute(
        select(Role).options(selectinload(Role.permissions)).where(Role.id == role_id)
    )
    role = result.scalars().first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    if role.is_system and body.name is not None and body.name != role.name:
        raise HTTPException(status_code=400, detail="Cannot rename a system role")

    if body.name is not None:
        role.name = body.name
    if body.description is not None:
        role.description = body.description
    if body.is_active is not None:
        role.is_active = body.is_active

    await db.flush()
    await db.refresh(role)
    return _role_to_out(role)


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(PermissionCode.ROLE_DELETE)),
):
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalars().first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    if role.is_system:
        raise HTTPException(status_code=400, detail="Cannot delete a system role")
    await db.delete(role)


@router.post("/{role_id}/permissions", response_model=RoleOut)
async def assign_permissions(
    role_id: str,
    permission_ids: list[str],
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(PermissionCode.ROLE_ASSIGN_PERMISSION)),
):
    result = await db.execute(
        select(Role).options(selectinload(Role.permissions)).where(Role.id == role_id)
    )
    role = result.scalars().first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    perms_result = await db.execute(select(Permission).where(Permission.id.in_(permission_ids)))
    role.permissions = perms_result.scalars().all()
    await db.flush()
    await db.refresh(role)
    return _role_to_out(role)


def _role_to_out(role: Role) -> RoleOut:
    return RoleOut(
        id=role.id,
        name=role.name,
        description=role.description,
        is_active=role.is_active,
        is_system=role.is_system,
        permissions=[PermissionOut(id=p.id, code=p.code, name=p.name, group=p.group) for p in role.permissions],
        created_at=role.created_at,
    )
