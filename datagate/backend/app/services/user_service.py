from fastapi import HTTPException, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, selectinload

from app.core.security import get_password_hash
from app.models.role import Role
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserOut,
    UserRoleAssign,
    UserUpdate,
)


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def list_users(
        self,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
    ) -> list[UserOut]:
        query = (
            self.db.query(User)
            .options(
                selectinload(User.roles).selectinload(Role.permissions)
            )
        )

        if search:
            query = query.filter(
                or_(
                    User.username.ilike(f"%{search}%"),
                    User.email.ilike(f"%{search}%"),
                    User.full_name.ilike(f"%{search}%"),
                )
            )

        total = query.with_entities(func.count(User.id)).scalar() or 0

        users = (
            query
            .order_by(User.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return [self.to_user_out(user) for user in users]

    def get_user_by_id(self, user_id: str) -> User | None:
        return (
            self.db.query(User)
            .options(
                selectinload(User.roles).selectinload(Role.permissions)
            )
            .filter(User.id == user_id)
            .first()
        )

    def get_user_or_404(self, user_id: str) -> User:
        user = self.get_user_by_id(user_id)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        return user

    def create_user(self, data: UserCreate) -> UserOut:
        existing_user = (
            self.db.query(User)
            .filter(
                or_(
                    User.username == data.username,
                    User.email == data.email,
                )
            )
            .first()
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already registered",
            )

        user = User(
            username=data.username,
            email=data.email,
            hashed_password=get_password_hash(data.password),
            full_name=data.full_name,
        )

        if data.role_ids:
            user.roles = self.get_roles_by_ids(data.role_ids)

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return self.to_user_out(user)

    def update_user(
        self,
        user_id: str,
        data: UserUpdate,
    ) -> UserOut:
        user = self.get_user_or_404(user_id)

        update_data = data.model_dump(exclude_unset=True)

        if "username" in update_data:
            existing_user = (
                self.db.query(User)
                .filter(
                    User.username == update_data["username"],
                    User.id != user.id,
                )
                .first()
            )

            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already registered",
                )

            user.username = update_data.pop("username")

        if "email" in update_data:
            existing_user = (
                self.db.query(User)
                .filter(
                    User.email == update_data["email"],
                    User.id != user.id,
                )
                .first()
            )

            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered",
                )

            user.email = update_data.pop("email")

        if "password" in update_data:
            password = update_data.pop("password")

            if password:
                user.hashed_password = get_password_hash(password)

        if "role_ids" in update_data:
            role_ids = update_data.pop("role_ids")

            if role_ids is not None:
                user.roles = self.get_roles_by_ids(role_ids)

        for field, value in update_data.items():
            setattr(user, field, value)

        self.db.commit()
        self.db.refresh(user)

        return self.to_user_out(user)

    def deactivate_user(
        self,
        user_id: str,
        current_user_id: str,
    ) -> None:
        user = self.get_user_or_404(user_id)

        if user.id == current_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot deactivate your own account",
            )

        user.is_active = False

        self.db.commit()

    def assign_roles(
        self,
        user_id: str,
        data: UserRoleAssign,
    ) -> UserOut:
        user = self.get_user_or_404(user_id)

        user.roles = self.get_roles_by_ids(data.role_ids)

        self.db.commit()
        self.db.refresh(user)

        return self.to_user_out(user)

    def get_roles_by_ids(self, role_ids: list[str]) -> list[Role]:
        if not role_ids:
            return []

        roles = (
            self.db.query(Role)
            .filter(Role.id.in_(role_ids))
            .all()
        )

        if len(roles) != len(set(role_ids)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Some roles do not exist",
            )

        return roles

    def get_permission_codes(self, user: User) -> set[str]:
        permission_codes = set()

        for role in user.roles:
            if not role.is_active:
                continue

            for permission in role.permissions:
                permission_codes.add(permission.code)

        return permission_codes

    def to_user_out(self, user: User) -> UserOut:
        return UserOut(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            roles=[
                role.name
                for role in user.roles
                if role.is_active
            ],
            permissions=sorted(self.get_permission_codes(user)),
            created_at=user.created_at,
            updated_at=user.updated_at,
        )