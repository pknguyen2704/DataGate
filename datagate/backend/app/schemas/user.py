from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str | None = None
    role_ids: list[str] = []


class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    full_name: str | None = None
    is_active: bool | None = None
    role_ids: list[str] | None = None


class UserOut(BaseModel):
    id: str
    username: str
    email: EmailStr
    full_name: str | None = None
    is_active: bool
    roles: list[str] = []
    permissions: list[str] = []
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class UserRoleAssign(BaseModel):
    role_ids: list[str]
