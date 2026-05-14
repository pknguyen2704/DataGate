from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.schemas.role_schema import RoleLiteOut
from app.schemas.common_schema import PaginatedResponse


class UserBase(BaseModel):
    username: str = Field(..., max_length=100)
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr
    is_active: bool = True


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=128)
    role_ids: list[UUID] = Field(default_factory=list)


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, max_length=100)
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=6, max_length=128)
    is_active: bool | None = None
    role_ids: list[UUID] | None = None


class UserProfileUpdate(BaseModel):
    username: str | None = Field(default=None, max_length=100)
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=6, max_length=128)


class UserRoleAssign(BaseModel):
    role_ids: list[UUID] = Field(default_factory=list)


class UserPasswordUpdate(BaseModel):
    password: str = Field(..., min_length=6, max_length=128)


class UserOut(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    roles: list[RoleLiteOut] = []
    model_config = ConfigDict(from_attributes=True)


class UserLiteOut(BaseModel):
    id: UUID
    username: str
    full_name: str | None = None
    email: EmailStr
    is_active: bool
    model_config = ConfigDict(from_attributes=True)


class UserListOut(PaginatedResponse[UserOut]):
    pass