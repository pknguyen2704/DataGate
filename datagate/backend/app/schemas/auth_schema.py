from pydantic import BaseModel, Field
from uuid import UUID

class LoginRequest(BaseModel):
    username: str = Field(..., max_length=50)
    password: str = Field(..., max_length=50)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str