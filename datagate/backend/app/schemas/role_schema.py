from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID

from app.schemas.common_schema import PaginatedResponse


class RoleBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: str | None = None


class RoleOut(RoleBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    permissions: list[str] = []

    model_config = ConfigDict(from_attributes=True)


class RoleLiteOut(BaseModel):
    id: UUID
    name: str

    model_config = ConfigDict(from_attributes=True)


class RoleListOut(PaginatedResponse[RoleOut]):
    pass
