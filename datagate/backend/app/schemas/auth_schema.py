from pydantic import BaseModel, EmailStr, Field
from uuid import UUID


class LoginRequest(BaseModel):
    username: str = Field(..., max_length=100)
    password: str = Field(..., min_length=6, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserMeOut"


class TokenPayload(BaseModel):
    sub: str | None = None


class UserMeOut(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    full_name: str | None = None
    roles: list[str] = []
    permissions: list[str] = []


class MessageResponse(BaseModel):
    message: str
