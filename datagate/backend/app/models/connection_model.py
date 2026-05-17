import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class Connection(Base):
    __tablename__ = "connections"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    connection_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    trino_host = Column(String(255), nullable=False)
    trino_port = Column(Integer, default=8080, nullable=False)
    trino_user = Column(String(255), nullable=False)
    trino_password = Column(Text, nullable=True)

    iceberg_rest_url = Column(String(255), nullable=False)
    iceberg_catalog_name = Column(String(255), nullable=False)
    iceberg_warehouse = Column(String(255), nullable=False)

    minio_endpoint_url = Column(String(255), nullable=False)
    minio_access_key = Column(String(255), nullable=False)
    minio_secret_key = Column(Text, nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)
    created_by = Column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    last_modified_by = Column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
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

    tables = relationship("Table", back_populates="connection")
    created_by_user = relationship("User", foreign_keys=[created_by])
    last_modified_by_user = relationship("User", foreign_keys=[last_modified_by])

    __table_args__ = (
        Index("ix_connections__connection_name", "connection_name", unique=True),
        Index("ix_connections__is_active", "is_active"),
        Index("ix_connections__created_by", "created_by"),
    )
