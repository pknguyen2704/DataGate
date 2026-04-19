from typing import Optional, List
from pydantic import BaseModel, EmailStr, ConfigDict, field_validator

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = True

class UserCreate(UserBase):
    email: EmailStr
    username: str
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserOut(UserBase):
    id: int
    is_superuser: bool = False
    roles: List[str] = []

    model_config = ConfigDict(from_attributes=True)

    @field_validator("roles", mode="before")
    @classmethod
    def transform_roles(cls, v):
        """Chuyển đổi danh sách đối tượng Role thành danh sách tên Role (string)."""
        if isinstance(v, list):
            return [role.name if hasattr(role, 'name') else str(role) for role in v]
        return v
