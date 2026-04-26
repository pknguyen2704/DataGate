"""
SQLAlchemy ORM Models — User, Role, Permission, RBAC join tables
"""
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Boolean, DateTime, ForeignKey, Table, Text, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base


def gen_uuid():
    return str(uuid.uuid4())


# Association table: users ↔ roles
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", UUID(as_uuid=False), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)

# Association table: roles ↔ permissions
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", UUID(as_uuid=False), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", UUID(as_uuid=False), ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    roles = relationship("Role", secondary=user_roles, back_populates="users", lazy="selectin")
    table_access = relationship("UserTableAccess", foreign_keys="[UserTableAccess.user_id]", back_populates="user", lazy="dynamic")

    @property
    def permission_codes(self) -> set:
        """Get all permission codes from all assigned roles."""
        codes = set()
        for role in self.roles:
            if role.is_active:
                for perm in role.permissions:
                    codes.add(perm.code)
        return codes

    def has_permission(self, code: str) -> bool:
        return code in self.permission_codes


class Role(Base):
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_system = Column(Boolean, default=False, nullable=False)  # system roles can't be deleted
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles", lazy="selectin")


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    code = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    group = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)

    # Relationships
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")
