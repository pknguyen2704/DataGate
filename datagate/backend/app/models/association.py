from sqlalchemy import Column, ForeignKey, Index, Table
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base


user_roles = Table(
    "user_roles",
    Base.metadata,
    Column(
        "user_id",
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "role_id",
        UUID(as_uuid=False),
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Index("ix_user_roles__role_id", "role_id"),
)


role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column(
        "role_id",
        UUID(as_uuid=False),
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "permission_id",
        UUID(as_uuid=False),
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Index("ix_role_permissions__permission_id", "permission_id"),
)
