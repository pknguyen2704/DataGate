import uuid

from sqlalchemy import Column, DateTime, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class Role(Base):
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)

    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    permissions = Column(JSONB, nullable=True)

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    users = relationship("User", back_populates="role", foreign_keys="User.role_id")

    __table_args__ = (
        Index("ix_roles__name", "name", unique=True),
    )
