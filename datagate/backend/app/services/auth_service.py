from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload

from app.core.security import create_access_token, verify_password
from app.models import Role, User
from app.schemas import LoginRequest, TokenResponse, UserMeOut


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_id(self, user_id: str) -> User | None:
        return (
            self.db.query(User)
            .options(selectinload(User.role))
            .filter(User.id == user_id)
            .first()
        )

    def get_user_by_username_or_email(self, username: str) -> User | None:
        return (
            self.db.query(User)
            .options(selectinload(User.role))
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

        access_token = create_access_token(user.id)

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=self.build_user_me(user),
        )

    def build_user_me(self, user: User) -> UserMeOut:
        return UserMeOut(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            roles=self.get_role_names(user),
            permissions=self.get_permission_codes(user),
        )

    def get_role_names(self, user: User) -> list[str]:
        return [user.role.name] if user.role else []

    def get_permission_codes(self, user: User) -> list[str]:
        permission_codes: set[str] = set()

        role = user.role
        if role:
            for permission_code in role.permissions or []:
                permission_codes.add(permission_code)

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

        if user.role and user.role.name == "Admin":
            return True

        return False
