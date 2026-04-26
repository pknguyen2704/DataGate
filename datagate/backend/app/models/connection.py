"""
SQLAlchemy ORM Models — Connection, TableInfo, UserTableAccess
"""
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Boolean, DateTime, ForeignKey, Text, Enum
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.base import Base


def gen_uuid():
    return str(uuid.uuid4())


class Connection(Base):
    __tablename__ = "connections"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    name = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    conn_type = Column(
        Enum("trino", "iceberg_rest", "minio", name="connection_type"),
        nullable=False
    )
    # Encrypted/masked config JSON
    config = Column(JSONB, nullable=False, default={})
    is_active = Column(Boolean, default=True, nullable=False)
    created_by = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    tables = relationship("TableInfo", back_populates="connection", lazy="dynamic")
    created_by_user = relationship("User", foreign_keys=[created_by])


class TableInfo(Base):
    __tablename__ = "table_info"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    connection_id = Column(UUID(as_uuid=False), ForeignKey("connections.id", ondelete="RESTRICT"), nullable=False)
    catalog_name = Column(String(255), nullable=False)
    schema_name = Column(String(255), nullable=False)
    table_name = Column(String(255), nullable=False)
    layer = Column(
        Enum("bronze", "silver", "gold", name="table_layer"),
        nullable=False,
        default="bronze"
    )
    description = Column(Text, nullable=True)
    owner_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    monitoring_enabled = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    connection = relationship("Connection", back_populates="tables")
    owner = relationship("User", foreign_keys=[owner_user_id])
    user_access = relationship("UserTableAccess", back_populates="table", lazy="dynamic")

    @property
    def full_name(self) -> str:
        return f"{self.catalog_name}.{self.schema_name}.{self.table_name}"


class UserTableAccess(Base):
    __tablename__ = "user_table_access"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    table_id = Column(UUID(as_uuid=False), ForeignKey("table_info.id", ondelete="CASCADE"), nullable=False)
    access_level = Column(
        Enum("view", "manage", name="table_access_level"),
        nullable=False,
        default="view"
    )
    granted_by = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    granted_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="table_access")
    table = relationship("TableInfo", back_populates="user_access")
    granter = relationship("User", foreign_keys=[granted_by])
