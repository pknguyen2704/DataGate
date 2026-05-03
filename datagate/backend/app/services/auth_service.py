from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload

from app.core.config import config
from app.core.security import create_access_token, verify_password
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, UserMeOut


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def login(self, data: LoginRequest) -> TokenResponse:
        user = self.get_user_by_username_or_email(data.username)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
            )

        if not verify_password(data.password, user.hashed_password):
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
            expires_delta=timedelta(minutes=config.access_token_expire_minutes),
        )

        return TokenResponse(access_token=token)

    def get_user_by_username_or_email(self, username_or_email: str) -> User | None:
        return (
            self.db.query(User)
            .options(selectinload(User.roles))
            .filter(
                or_(
                    User.username == username_or_email,
                    User.email == username_or_email,
                )
            )
            .first()
        )

    def build_user_me(self, user: User) -> UserMeOut:
        return UserMeOut(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            roles=self.get_role_names(user),
            permissions=sorted(self.get_permission_codes(user)),
        )

    def get_role_names(self, user: User) -> list[str]:
        return [
            role.name
            for role in user.roles
            if role.is_active
        ]

    def get_permission_codes(self, user: User) -> set[str]:
        permission_codes = set()

        for role in user.roles:
            if not role.is_active:
                continue

            for permission in role.permissions:
                permission_codes.add(permission.code)

        return permission_codes

    def has_permission(self, user: User, permission_code: str) -> bool:
        permission_codes = self.get_permission_codes(user)

        if "admin" in permission_codes:
            return True

        return permission_code in permission_codes

    def is_admin(self, user: User) -> bool:
        return "admin" in self.get_permission_codes(user)
