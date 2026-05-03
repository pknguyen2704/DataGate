import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class Connection(Base):
    __tablename__ = "connections"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)

    name = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)

    trino_host = Column(String(255), nullable=False)
    trino_port = Column(Integer, default=8080, nullable=False)
    trino_user = Column(String(255), nullable=False)
    trino_password = Column(String(255), nullable=True)

    iceberg_rest_url = Column(String(255), nullable=False)
    iceberg_catalog_name = Column(String(255), nullable=False)

    minio_endpoint_url = Column(String(255), nullable=False)
    minio_access_key = Column(String(255), nullable=False)
    minio_secret_key = Column(String(255), nullable=False)
    minio_region = Column(String(50), default="us-east-1", nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)

    created_by = Column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    tables = relationship(
        "Table",
        back_populates="connection",
    )

    created_by_user = relationship(
        "User",
        foreign_keys=[created_by],
    )