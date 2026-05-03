# Role & Permission domain schemas.
from __future__ import annotations
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PermissionOut(BaseModel):
    id: str
    code: str
    name: str
    group: Optional[str] = None
    description: Optional[str] = None

    model_config = {"from_attributes": True}


class RoleOut(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    is_active: bool
    is_system: bool
    permissions: list[PermissionOut] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    permission_ids: list[str] = []


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    permission_ids: Optional[list[str]] = None


class PermissionAssign(BaseModel):
    """Body for POST /roles/{role_id}/permissions."""
    permission_ids: list[str]
