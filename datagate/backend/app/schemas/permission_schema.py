from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID


class PermissionBase(BaseModel):
    code: str = Field(..., max_length=100)
    name: str = Field(..., max_length=255)
    permission_group: str | None = Field(default=None, max_length=100)
    description: str | None = None


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(BaseModel):
    code: str | None = Field(default=None, max_length=100)
    name: str | None = Field(default=None, max_length=255)
    permission_group: str | None = Field(default=None, max_length=100)
    description: str | None = None


class PermissionOut(PermissionBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)


class PermissionLiteOut(BaseModel):
    id: UUID
    code: str
    name: str

    model_config = ConfigDict(from_attributes=True)