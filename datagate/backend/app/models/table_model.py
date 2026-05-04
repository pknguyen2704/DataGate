import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class Table(Base):
    __tablename__ = "tables"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)

    connection_id = Column(
        UUID(as_uuid=False),
        ForeignKey("connections.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    catalog_name = Column(String(255), nullable=False)
    schema_name = Column(String(255), nullable=False)
    table_name = Column(String(255), nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    connection = relationship(
        "Connection",
        back_populates="tables",
    )

    batch_table_metadata = relationship(
        "BatchTableMetadata",
        back_populates="table",
        cascade="all, delete-orphan",
    )

    batch_table_profiling = relationship(
        "BatchTableProfiling",
        back_populates="table",
        cascade="all, delete-orphan",
    )

    metric_manual_thresholds = relationship(
        "MetricManualThreshold",
        back_populates="table",
        cascade="all, delete-orphan",
    )

    rules = relationship(
        "Rule",
        back_populates="table",
        cascade="all, delete-orphan",
    )

    anomaly_results = relationship(
        "AnomalyResult",
        back_populates="table",
        cascade="all, delete-orphan",
    )

    lightgbm_parameters = relationship(
        "LightGBMParameter",
        back_populates="table",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint(
            "connection_id",
            "catalog_name",
            "schema_name",
            "table_name",
            name="uq_table_connection_id_catalog_name_schema_name_table_name",
        ),
    )