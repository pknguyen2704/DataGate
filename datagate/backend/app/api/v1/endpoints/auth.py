"""
Auth endpoints — login, /me, logout
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from datetime import timedelta

from app.db.session import get_db
from app.core.security import verify_password, create_access_token, get_password_hash
from app.core.config import settings
from app.models.auth import User
from app.api.deps import get_current_user

router = APIRouter()


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: str
    username: str
    email: str
    full_name: str | None
    is_active: bool
    permissions: list[str]
    roles: list[str]

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    username: str  # accepts username or email
    password: str


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate with username/email + password."""
    result = await db.execute(
        select(User)
        .options(selectinload(User.roles))
        .where(
            or_(
                User.username == form_data.username,
                User.email == form_data.username,
            )
        )
    )
    user = result.scalars().first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )

    token = create_access_token(
        subject=user.id,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    """Return the currently authenticated user."""
    return UserOut(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        permissions=list(current_user.permission_codes),
        roles=[r.name for r in current_user.roles if r.is_active],
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout():
    """Logout (client-side token removal)."""
    return None
