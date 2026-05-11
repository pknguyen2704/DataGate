from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID

from app.schemas.permission_schema import PermissionLiteOut


class RoleBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: str | None = None
    is_active: bool = True
    is_system: bool = False


class RoleCreate(RoleBase):
    permission_ids: list[UUID] = Field(default_factory=list)


class RoleUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=100)
    description: str | None = None
    is_active: bool | None = None
    is_system: bool | None = None
    permission_ids: list[UUID] | None = None


class PermissionAssign(BaseModel):
    permission_ids: list[UUID] = Field(default_factory=list)


class RoleOut(RoleBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    permissions: list[PermissionLiteOut] = []

    model_config = ConfigDict(from_attributes=True)


class RoleLiteOut(BaseModel):
    id: UUID
    name: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
