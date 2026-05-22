import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class Table(Base):
    __tablename__ = "tables"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    # Cascade xoa connection thi xoa toan bo bang
    connection_id = Column(UUID(as_uuid=False),ForeignKey("connections.id", ondelete="CASCADE"),nullable=False)

    catalog_name = Column(String(255), nullable=False)
    schema_name = Column(String(255), nullable=False)
    table_name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now(),nullable=False)

    # Relationship
    connection = relationship("Connection", back_populates="tables")
    batch_table_metadata = relationship(
        "BatchTableMetadata", back_populates="table", cascade="all, delete-orphan"
    )
    batch_table_profiling = relationship(
        "BatchTableProfiling", back_populates="table", cascade="all, delete-orphan"
    )
    quality_thresholds = relationship(
        "QualityThreshold", back_populates="table", cascade="all, delete-orphan"
    )
    rules = relationship("Rule", back_populates="table", cascade="all, delete-orphan")
    quality_check_results = relationship(
        "QualityCheckResult", back_populates="table", cascade="all, delete-orphan"
    )
    anomaly_config = relationship(
        "AnomalyConfig",
        back_populates="table",
        uselist=False,
        cascade="all, delete-orphan",
    )
    anomaly_results = relationship(
        "AnomalyResult", back_populates="table", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index(
            "ix_tables__connection_catalog_schema_table",
            "connection_id",
            "catalog_name",
            "schema_name",
            "table_name",
            unique=True,
        ),
        Index("ix_tables__connection_id", "connection_id"),
        Index("ix_tables__is_active", "is_active"),
    )
