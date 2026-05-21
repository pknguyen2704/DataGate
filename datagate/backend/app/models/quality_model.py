import uuid

from sqlalchemy import (
    Boolean,
    BigInteger,
    Column,
    DateTime,
    Float,
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


class BatchTableMetadata(Base):
    __tablename__ = "batch_table_metadata"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    table_id = Column(UUID(as_uuid=False), ForeignKey("tables.id", ondelete="CASCADE"), nullable=False)

    batch_added_rows = Column(BigInteger, nullable=True)
    batch_added_files = Column(Integer, nullable=True)
    batch_added_files_size_bytes = Column(BigInteger, nullable=True)
    table_total_rows = Column(BigInteger, nullable=True)
    table_total_files = Column(Integer, nullable=True)
    table_total_size_bytes = Column(BigInteger, nullable=True)

    processing_date_hour = Column(DateTime, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    table = relationship("Table", back_populates="batch_table_metadata")

    __table_args__ = (
        Index(
            "ix_batch_table_metadata__table_hour",
            "table_id",
            "processing_date_hour",
            unique=True,
        ),
        Index("ix_batch_table_metadata__processing_date_hour", "processing_date_hour"),
    )


class BatchTableProfiling(Base):
    __tablename__ = "batch_table_profiling"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    table_id = Column(UUID(as_uuid=False), ForeignKey("tables.id", ondelete="CASCADE"), nullable=False)

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
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    table = relationship("Table", back_populates="batch_table_profiling")

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


class QualityThreshold(Base):
    __tablename__ = "quality_thresholds"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    table_id = Column(UUID(as_uuid=False), ForeignKey("tables.id", ondelete="CASCADE"), nullable=False)

    check_type = Column(String(50), nullable=False)
    column_name = Column(String(255), nullable=True)
    metric_name = Column(String(255), nullable=False)

    min_threshold = Column(Float, nullable=True)
    max_threshold = Column(Float, nullable=True)

    severity_level = Column(String(50),nullable=False,default="warning")
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

    table = relationship("Table", back_populates="quality_thresholds")
    results = relationship("QualityCheckResult", back_populates="threshold")
    created_by_user = relationship("User", foreign_keys=[created_by])
    last_modified_by_user = relationship("User", foreign_keys=[last_modified_by])

    __table_args__ = (
        Index(
            "ix_quality_thresholds__table_type_column_metric",
            "table_id",
            "check_type",
            "column_name",
            "metric_name",
            unique=True,
        ),
        Index("ix_quality_thresholds__table_active", "table_id", "is_active"),
    )


class QualityCheckResult(Base):
    __tablename__ = "quality_check_results"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    table_id = Column(UUID(as_uuid=False), ForeignKey("tables.id", ondelete="CASCADE"), nullable=False)

    check_type = Column(String(50), nullable=False)
    threshold_id = Column(UUID(as_uuid=False),ForeignKey("quality_thresholds.id", ondelete="SET NULL"), nullable=True)
    rule_id = Column(UUID(as_uuid=False), ForeignKey("rules.id", ondelete="SET NULL"), nullable=True)
    anomaly_result_id = Column(UUID(as_uuid=False),ForeignKey("anomaly_results.id", ondelete="SET NULL"),nullable=True)

    column_name = Column(String(255), nullable=True)
    metric_name = Column(String(255), nullable=True)
    actual_value = Column(Float, nullable=True)
    min_threshold = Column(Float, nullable=True)
    max_threshold = Column(Float, nullable=True)

    status = Column(String(50), nullable=False)
    severity_level = Column(String(50),nullable=False,default="warning")
    message = Column(Text, nullable=True)

    is_resolved = Column(Boolean, default=False, nullable=False)
    resolved_by = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    processing_date_hour = Column(DateTime, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    table = relationship("Table", back_populates="quality_check_results")
    threshold = relationship("QualityThreshold", back_populates="results")
    rule = relationship("Rule", back_populates="quality_check_results")
    anomaly_result = relationship(
        "AnomalyResult", back_populates="quality_check_results"
    )
    resolved_by_user = relationship("User", foreign_keys=[resolved_by])

    __table_args__ = (
        Index(
            "ix_quality_check_results__table_hour",
            "table_id",
            "processing_date_hour",
        ),
        Index(
            "ix_quality_check_results__table_type_hour",
            "table_id",
            "check_type",
            "processing_date_hour",
        ),
        Index(
            "ix_quality_check_results__status_severity_hour",
            "status",
            "severity_level",
            "processing_date_hour",
        ),
        Index("ix_quality_check_results__is_resolved", "is_resolved"),
        Index(
            "uq_quality_check_results__threshold_hour",
            "table_id",
            "check_type",
            "threshold_id",
            "processing_date_hour",
            unique=True,
            postgresql_where="threshold_id IS NOT NULL",
        ),
        Index(
            "uq_quality_check_results__rule_hour",
            "table_id",
            "check_type",
            "rule_id",
            "processing_date_hour",
            unique=True,
            postgresql_where="rule_id IS NOT NULL",
        ),
    )
