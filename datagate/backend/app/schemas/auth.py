from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserMeOut(BaseModel):
    id: str
    username: str
    email: EmailStr
    full_name: str | None = None
    is_active: bool
    roles: list[str] = []
    permissions: list[str] = []