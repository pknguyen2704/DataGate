import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class Table(Base):
    __tablename__ = "tables"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    connection_id = Column(UUID(as_uuid=False), ForeignKey("connections.id", ondelete="RESTRICT"), nullable=False)

    catalog_name = Column(String(255), nullable=False)
    schema_name = Column(String(255), nullable=False)
    table_name = Column(String(255), nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    connection = relationship("Connection", back_populates="tables")
    batch_table_metadata = relationship("BatchTableMetadata", back_populates="table", cascade="all, delete-orphan")
    batch_table_profiling = relationship("BatchTableProfiling", back_populates="table", cascade="all, delete-orphan")
    batch_table_metadata_manual_thresholds = relationship("BatchTableMetadataManualThreshold", back_populates="table", cascade="all, delete-orphan")
    batch_table_profiling_manual_thresholds = relationship("BatchTableProfilingManualThreshold", back_populates="table", cascade="all, delete-orphan")
    rules = relationship("Rule", back_populates="table", cascade="all, delete-orphan")
    lightgbm_parameter = relationship("LightGBMParameter", back_populates="table", uselist=False, cascade="all, delete-orphan")
    lightgbm_auc = relationship("LightGBMAUC", back_populates="table", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_tables__connection_catalog_schema_table", "connection_id", "catalog_name", "schema_name", "table_name", unique=True),
        Index("ix_tables__connection_id", "connection_id"),
        Index("ix_tables__is_active", "is_active"),
    )