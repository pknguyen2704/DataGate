from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload

from app.core.security import create_access_token, get_password_hash, verify_password
from app.models import Role, User
from app.schemas import ChangePasswordRequest, LoginRequest, TokenResponse, UserMeOut


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_id(self, user_id: str) -> User | None:
        return (
            self.db.query(User)
            .options(selectinload(User.roles).selectinload(Role.permissions))
            .filter(User.id == user_id)
            .first()
        )

    def get_user_by_username_or_email(self, username: str) -> User | None:
        return (
            self.db.query(User)
            .options(selectinload(User.roles).selectinload(Role.permissions))
            .filter(
                or_(
                    User.username == username,
                    User.email == username,
                )
            )
            .first()
        )

    def login(self, data: LoginRequest) -> TokenResponse:
        user = self.get_user_by_username_or_email(data.username)

        if not user or not verify_password(data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username/email or password",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user",
            )

        return TokenResponse(
            access_token=create_access_token(user.id),
            token_type="bearer",
        )

    def build_user_me(self, user: User) -> UserMeOut:
        return UserMeOut(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            roles=self.get_role_names(user),
            permissions=self.get_permission_codes(user),
        )

    def get_role_names(self, user: User) -> list[str]:
        return [
            role.name
            for role in user.roles
            if role.is_active
        ]

    def get_permission_codes(self, user: User) -> list[str]:
        permission_codes: set[str] = set()

        for role in user.roles:
            if not role.is_active:
                continue

            for permission in role.permissions:
                permission_codes.add(permission.code)

        return sorted(permission_codes)

    def has_permission(self, user: User, permission_code: str) -> bool:
        permission_codes = self.get_permission_codes(user)

        if permission_code in permission_codes:
            return True

        module_name = permission_code.split(":")[0]

        if f"{module_name}:*" in permission_codes:
            return True

        if "admin:*" in permission_codes:
            return True

        return False

    def change_password(
        self,
        user: User,
        data: ChangePasswordRequest,
    ) -> None:
        if not verify_password(data.current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect",
            )

        user.hashed_password = get_password_hash(data.new_password)

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)