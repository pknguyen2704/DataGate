from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.schemas.role_schema import RoleLiteOut
from app.schemas.common_schema import PaginatedResponse


class UserBase(BaseModel):
    username: str = Field(..., max_length=100)
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=128)
    role_id: UUID


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, max_length=100)
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=6, max_length=128)
    role_id: UUID | None = None


class UserProfileUpdate(BaseModel):
    username: str | None = Field(default=None, max_length=100)
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=6, max_length=128)


class UserOut(UserBase):
    id: UUID
    role_id: UUID
    created_at: datetime
    updated_at: datetime
    role: RoleLiteOut | None = None
    roles: list[RoleLiteOut] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)


class UserLiteOut(BaseModel):
    id: UUID
    username: str
    full_name: str | None = None
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)


class UserListOut(PaginatedResponse[UserOut]):
    pass
