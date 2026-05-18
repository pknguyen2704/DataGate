import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    username = Column(String(100), nullable=False)
    full_name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role_id = Column(
        UUID(as_uuid=False), ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False
    )
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    role = relationship("Role", back_populates="users", foreign_keys=[role_id])
    __table_args__ = (
        Index("ix_users__email", "email", unique=True),
        Index("ix_users__role_id", "role_id"),
        Index("ix_users__username", "username", unique=True),
    )
