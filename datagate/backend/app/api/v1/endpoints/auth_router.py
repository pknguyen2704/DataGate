from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import User
from app.schemas import (
    ChangePasswordRequest,
    LoginRequest,
    MessageResponse,
    TokenResponse,
    UserMeOut,
)
from app.services import AuthService


auth_router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


def get_auth_service(
    db: Session = Depends(get_db),
) -> AuthService:
    return AuthService(db)


@auth_router.post("/login", response_model=TokenResponse)
def login(
    data: LoginRequest,
    service: AuthService = Depends(get_auth_service),
):
    return service.login(data)


@auth_router.get("/me", response_model=UserMeOut)
def get_me(
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
):
    return service.build_user_me(current_user)


@auth_router.post("/change-password", response_model=MessageResponse)
def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
):
    service.change_password(current_user, data)

    return MessageResponse(
        message="Password changed successfully",
    )


@auth_router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout():
    return None