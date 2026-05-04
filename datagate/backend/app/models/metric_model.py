import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class MetricManualThreshold(Base):
    __tablename__ = "metric_manual_thresholds"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)

    table_id = Column(
        UUID(as_uuid=False),
        ForeignKey("tables.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    metric_group = Column(
        Enum(
            "metadata",
            "profiling",
            name="metric_manual_threshold_group",
        ),
        nullable=False,
        index=True,
    )

    # Metadata metric: column_name = "__table__"
    # Profiling metric: column_name = real column name
    column_name = Column(String(255), nullable=False, default="__table__")

    metric_name = Column(String(255), nullable=False, index=True)

    min_threshold = Column(Float, nullable=True)
    max_threshold = Column(Float, nullable=True)

    severity_level = Column(
        Enum(
            "warning",
            "critical",
            name="manual_threshold_severity_level",
        ),
        nullable=False,
        default="warning",
        index=True,
    )

    is_active = Column(Boolean, default=True, nullable=False)

    description = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    table = relationship(
        "Table",
        back_populates="metric_manual_thresholds",
    )

    results = relationship(
        "MetricResult",
        back_populates="metric_manual_threshold",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint(
            "table_id",
            "metric_group",
            "column_name",
            "metric_name",
            name="uq_metric_manual_threshold_table_group_column_metric",
        ),
        Index(
            "ix_metric_manual_threshold_lookup",
            "table_id",
            "metric_group",
            "column_name",
            "metric_name",
            "is_active",
        ),
    )


class MetricResult(Base):
    __tablename__ = "metric_results"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)

    metric_manual_threshold_id = Column(
        UUID(as_uuid=False),
        ForeignKey("metric_manual_thresholds.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    actual_value = Column(Float, nullable=True)
    status = Column(
        Enum(
            "pass",
            "fail",
            name="metric_result_status",
        ),
        nullable=False,
        index=True,
    )

    min_threshold = Column(Float, nullable=True)
    max_threshold = Column(Float, nullable=True)

    severity_level = Column(
        Enum(
            "warning",
            "critical",
            name="manual_threshold_severity_level",
        ),
        nullable=True,
        index=True,
    )

    processing_date_hour = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    metric_manual_threshold = relationship(
        "MetricManualThreshold",
        back_populates="results",
    )

    __table_args__ = (
        UniqueConstraint(
            "metric_manual_threshold_id",
            "processing_date_hour",
            name="uq_metric_result_threshold_hour",
        ),
        Index(
            "ix_metric_result_threshold_hour",
            "metric_manual_threshold_id",
            "processing_date_hour",
        ),
        Index(
            "ix_metric_result_status_hour",
            "status",
            "processing_date_hour",
        ),
    )