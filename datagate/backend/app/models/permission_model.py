import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Index, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.association import role_permissions


def gen_uuid() -> str:
    return str(uuid.uuid4())


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    code = Column(String(100), nullable=False)
    name = Column(String(255), nullable=False)
    permission_group = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")

    __table_args__ = (
        Index("ix_permissions__code", "code", unique=True),
        Index("ix_permissions__permission_group", "permission_group"),
    )