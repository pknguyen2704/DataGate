import uuid

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
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class QualityMetricObservation(Base):
    __tablename__ = "quality_metric_observations"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    table_id = Column(
        UUID(as_uuid=False), ForeignKey("tables.id", ondelete="CASCADE"), nullable=False
    )

    metric_scope = Column(
        Enum("metadata", "profiling", "anomaly", name="metric_scope"),
        nullable=False,
    )
    column_name = Column(String(255), nullable=True)
    metric_name = Column(String(255), nullable=False)
    metric_value = Column(Float, nullable=True)
    extra_data = Column(JSONB, nullable=True)

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

    table = relationship("Table", back_populates="quality_metric_observations")

    __table_args__ = (
        Index(
            "ix_quality_metric_observations__table_hour_scope_column_metric",
            "table_id",
            "processing_date_hour",
            "metric_scope",
            "column_name",
            "metric_name",
            unique=True,
        ),
        Index(
            "ix_quality_metric_observations__table_hour",
            "table_id",
            "processing_date_hour",
        ),
        Index(
            "ix_quality_metric_observations__table_scope_metric",
            "table_id",
            "metric_scope",
            "metric_name",
        ),
    )


class QualityThreshold(Base):
    __tablename__ = "quality_thresholds"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    table_id = Column(
        UUID(as_uuid=False), ForeignKey("tables.id", ondelete="CASCADE"), nullable=False
    )

    metric_scope = Column(
        Enum("metadata", "profiling", "anomaly", name="metric_scope"),
        nullable=False,
    )
    column_name = Column(String(255), nullable=True)
    metric_name = Column(String(255), nullable=False)

    min_threshold = Column(Float, nullable=True)
    max_threshold = Column(Float, nullable=True)

    severity_level = Column(
        Enum("warning", "critical", name="severity_level"),
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

    table = relationship("Table", back_populates="quality_thresholds")
    results = relationship("QualityCheckResult", back_populates="threshold")
    created_by_user = relationship("User", foreign_keys=[created_by])
    last_modified_by_user = relationship("User", foreign_keys=[last_modified_by])

    __table_args__ = (
        Index(
            "ix_quality_thresholds__table_scope_column_metric",
            "table_id",
            "metric_scope",
            "column_name",
            "metric_name",
            unique=True,
        ),
        Index("ix_quality_thresholds__table_active", "table_id", "is_active"),
    )


class QualityCheckResult(Base):
    __tablename__ = "quality_check_results"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    table_id = Column(
        UUID(as_uuid=False), ForeignKey("tables.id", ondelete="CASCADE"), nullable=False
    )

    check_type = Column(
        Enum(
            "metadata_threshold",
            "profiling_threshold",
            "rule",
            "anomaly_auc",
            name="check_type",
        ),
        nullable=False,
    )
    threshold_id = Column(
        UUID(as_uuid=False),
        ForeignKey("quality_thresholds.id", ondelete="SET NULL"),
        nullable=True,
    )
    rule_id = Column(
        UUID(as_uuid=False), ForeignKey("rules.id", ondelete="SET NULL"), nullable=True
    )
    anomaly_result_id = Column(
        UUID(as_uuid=False),
        ForeignKey("anomaly_results.id", ondelete="SET NULL"),
        nullable=True,
    )

    column_name = Column(String(255), nullable=True)
    metric_name = Column(String(255), nullable=True)
    actual_value = Column(Float, nullable=True)
    min_threshold = Column(Float, nullable=True)
    max_threshold = Column(Float, nullable=True)

    status = Column(Enum("pass", "fail", "error", name="check_status"), nullable=False)
    severity_level = Column(
        Enum("warning", "critical", name="severity_level"), nullable=True
    )
    message = Column(Text, nullable=True)

    is_resolved = Column(Boolean, default=False, nullable=False)
    resolved_by = Column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    resolved_at = Column(DateTime(timezone=True), nullable=True)

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
    )
