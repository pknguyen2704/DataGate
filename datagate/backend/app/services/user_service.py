from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, selectinload

from app.core.security import get_hashed_password
from app.models import Role, User
from app.schemas.user_schema import (
    UserCreate,
    UserListOut,
    UserOut,
    UserProfileUpdate,
    UserUpdate,
)


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def _validate_unique_user(
        self, username: str | None, email: str | None, exclude_id: str | None = None
    ) -> None:
        filters = []
        if username:
            filters.append(User.username == username)
        if email:
            filters.append(User.email == email)
        if not filters:
            return
        query = self.db.query(User).filter(or_(*filters))
        if exclude_id:
            query = query.filter(User.id != exclude_id)
        if query.first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already registered",
            )

    def list_users(
        self, page: int = 1, page_size: int = 20, search: str | None = None
    ) -> UserListOut:
        query = self.db.query(User).options(selectinload(User.role))
        if search:
            keyword = f"%{search}%"
            query = query.filter(
                or_(
                    User.username.ilike(keyword),
                    User.email.ilike(keyword),
                    User.full_name.ilike(keyword),
                )
            )
        total = query.with_entities(func.count(User.id)).scalar() or 0
        users = (
            query.order_by(User.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return UserListOut(
            items=[self.to_user_out(user) for user in users],
            total=total,
            page=page,
            page_size=page_size,
        )

    def get_user_by_id(self, user_id: str) -> User | None:
        return (
            self.db.query(User)
            .options(selectinload(User.role))
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
        self._validate_unique_user(data.username, data.email)
        user = User(
            username=data.username,
            full_name=data.full_name,
            email=data.email,
            hashed_password=get_hashed_password(data.password),
            role=self.get_role_by_id(data.role_id),
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return self.to_user_out(self.get_user_or_404(str(user.id)))

    def update_user(
        self, user_id: str, data: UserUpdate | UserProfileUpdate
    ) -> UserOut:
        user = self.get_user_or_404(user_id)
        update_data = data.model_dump(exclude_unset=True)
        self._validate_unique_user(
            username=update_data.get("username"),
            email=update_data.get("email"),
            exclude_id=user_id,
        )
        if "password" in update_data:
            password = update_data.pop("password")
            if password:
                user.hashed_password = get_hashed_password(password)
        if "role_id" in update_data:
            role_id = update_data.pop("role_id")
            if role_id is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User must have exactly one role",
                )
            user.role = self.get_role_by_id(role_id)
        for field, value in update_data.items():
            setattr(user, field, value)
        self.db.commit()
        self.db.refresh(user)
        return self.to_user_out(self.get_user_or_404(str(user.id)))

    def get_role_by_id(self, role_id: UUID | str) -> Role:
        role = (
            self.db.query(Role)
            .filter(Role.id == str(role_id))
            .first()
        )
        if role is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role does not exist",
            )
        return role

    def get_permission_codes(self, user: User) -> set[str]:
        permission_codes = set()
        role = user.role
        if role:
            for permission in role.permissions or []:
                permission_codes.add(permission)
        return permission_codes

    def to_user_out(self, user: User) -> UserOut:
        data = UserOut.model_validate(user)
        data.roles = [data.role] if data.role else []
        return data
