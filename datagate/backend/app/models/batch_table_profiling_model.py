import uuid

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    func,
    Enum,
    Boolean,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class BatchTableProfiling(Base):
    __tablename__ = "batch_table_profiling"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    table_id = Column(
        UUID(as_uuid=False), ForeignKey("tables.id", ondelete="CASCADE"), nullable=False
    )

    column_name = Column(String(255), nullable=False)
    data_type = Column(String(100), nullable=True)

    completeness = Column(Float, nullable=True)
    mean = Column(Float, nullable=True)
    standard_deviation = Column(Float, nullable=True)
    minimum = Column(Float, nullable=True)
    maximum = Column(Float, nullable=True)

    min_length = Column(Integer, nullable=True)
    max_length = Column(Integer, nullable=True)

    distinctness = Column(Float, nullable=True)
    approx_count_distinct = Column(BigInteger, nullable=True)

    processing_date_hour = Column(DateTime, nullable=False)

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    table = relationship("Table", back_populates="batch_table_profiling")
    batch_table_profiling_metrics_verify = relationship(
        "BatchTableProfilingMetricsVerify",
        back_populates="batch_table_profiling",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index(
            "ix_batch_table_profiling__table_hour_column",
            "table_id",
            "processing_date_hour",
            "column_name",
            unique=True,
        ),
        Index(
            "ix_batch_table_profiling__table_column_hour",
            "table_id",
            "column_name",
            "processing_date_hour",
        ),
        Index("ix_batch_table_profiling__processing_date_hour", "processing_date_hour"),
    )


class BatchTableProfilingManualThreshold(Base):
    __tablename__ = "batch_table_profiling_manual_thresholds"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    table_id = Column(
        UUID(as_uuid=False), ForeignKey("tables.id", ondelete="CASCADE"), nullable=False
    )

    column_name = Column(String(255), nullable=False)
    metric_name = Column(String(255), nullable=False)

    min_threshold = Column(Float, nullable=True)
    max_threshold = Column(Float, nullable=True)

    severity_level = Column(
        Enum("warning", "critical", name="manual_threshold_severity_level"),
        nullable=False,
        default="warning",
    )
    is_active = Column(Boolean, default=True, nullable=False)
    description = Column(Text, nullable=True)

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

    table = relationship(
        "Table", back_populates="batch_table_profiling_manual_thresholds"
    )
    results = relationship(
        "BatchTableProfilingMetricsVerify",
        back_populates="profiling_manual_threshold",
        cascade="all, delete-orphan",
    )
    created_by_user = relationship("User", foreign_keys=[created_by])
    last_modified_by_user = relationship("User", foreign_keys=[last_modified_by])

    __table_args__ = (
        Index(
            "ix_batch_table_profiling_manual_thresholds__table_column_metric",
            "table_id",
            "column_name",
            "metric_name",
            unique=True,
        ),
        Index(
            "ix_batch_table_profiling_manual_thresholds__table_active",
            "table_id",
            "is_active",
        ),
        Index(
            "ix_batch_table_profiling_manual_thresholds__lookup",
            "table_id",
            "column_name",
            "metric_name",
            "is_active",
        ),
    )


class BatchTableProfilingMetricsVerify(Base):
    __tablename__ = "batch_table_profiling_metrics_verify"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)

    profiling_manual_threshold_id = Column(
        UUID(as_uuid=False),
        ForeignKey("batch_table_profiling_manual_thresholds.id", ondelete="CASCADE"),
        nullable=False,
    )
    batch_table_profiling_id = Column(
        UUID(as_uuid=False),
        ForeignKey("batch_table_profiling.id", ondelete="CASCADE"),
        nullable=False,
    )

    actual_value = Column(Float, nullable=True)
    status = Column(Enum("pass", "fail", name="metric_result_status"), nullable=False)

    min_threshold = Column(Float, nullable=True)
    max_threshold = Column(Float, nullable=True)
    severity_level = Column(
        Enum("warning", "critical", name="manual_threshold_severity_level"),
        nullable=True,
    )

    is_resolved = Column(Boolean, default=False, nullable=False)
    resolved_by = Column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    processing_date_hour = Column(DateTime, nullable=False)

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    profiling_manual_threshold = relationship(
        "BatchTableProfilingManualThreshold", back_populates="results"
    )
    batch_table_profiling = relationship(
        "BatchTableProfiling", back_populates="batch_table_profiling_metrics_verify"
    )
    resolved_by_user = relationship("User", foreign_keys=[resolved_by])

    __table_args__ = (
        Index(
            "ix_batch_table_profiling_metrics_verify__threshold_batch_unique",
            "profiling_manual_threshold_id",
            "batch_table_profiling_id",
            unique=True,
        ),
        Index(
            "ix_batch_table_profiling_metrics_verify__threshold_batch",
            "profiling_manual_threshold_id",
            "batch_table_profiling_id",
        ),
        Index(
            "ix_batch_table_profiling_metrics_verify__batch_status",
            "batch_table_profiling_id",
            "status",
        ),
    )
