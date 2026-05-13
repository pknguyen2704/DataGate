import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Index, Integer, func, String, Float, Enum, Boolean, Text
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
    batch_table_metadata_metrics_verify = relationship("BatchTableMetadataMetricsVerify", back_populates="batch_table_metadata", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_batch_table_metadata__table_hour", "table_id", "processing_date_hour", unique=True),
        Index("ix_batch_table_metadata__processing_date_hour", "processing_date_hour"),
    )

class BatchTableMetadataManualThreshold(Base):
    __tablename__ = "batch_table_metadata_manual_thresholds"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    table_id = Column(UUID(as_uuid=False), ForeignKey("tables.id", ondelete="CASCADE"), nullable=False)

    metric_name = Column(String(255), nullable=False)
    min_threshold = Column(Float, nullable=True)
    max_threshold = Column(Float, nullable=True)

    severity_level = Column(Enum("warning", "critical", name="manual_threshold_severity_level"), nullable=False, default="warning")
    is_active = Column(Boolean, default=True, nullable=False)
    description = Column(Text, nullable=True)

    created_by = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    last_modified_by = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    table = relationship("Table", back_populates="batch_table_metadata_manual_thresholds")
    results = relationship("BatchTableMetadataMetricsVerify", back_populates="metadata_manual_threshold", cascade="all, delete-orphan")
    created_by_user = relationship("User", foreign_keys=[created_by])
    last_modified_by_user = relationship("User", foreign_keys=[last_modified_by])

    __table_args__ = (
        Index("ix_batch_table_metadata_manual_thresholds__table_metric", "table_id", "metric_name", unique=True),
        Index("ix_batch_table_metadata_manual_thresholds__table_active", "table_id", "is_active"),
        Index("ix_batch_table_metadata_manual_thresholds__lookup", "table_id", "metric_name", "is_active"),
    )

class BatchTableMetadataMetricsVerify(Base):
    __tablename__ = "batch_table_metadata_metrics_verify"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)

    metadata_manual_threshold_id = Column(UUID(as_uuid=False), ForeignKey("batch_table_metadata_manual_thresholds.id", ondelete="CASCADE"), nullable=False)
    batch_table_metadata_id = Column(UUID(as_uuid=False), ForeignKey("batch_table_metadata.id", ondelete="CASCADE"), nullable=False)

    actual_value = Column(Float, nullable=True)
    status = Column(Enum("pass", "fail", name="metric_result_status"), nullable=False)

    min_threshold = Column(Float, nullable=True)
    max_threshold = Column(Float, nullable=True)
    severity_level = Column(Enum("warning", "critical", name="manual_threshold_severity_level"), nullable=True)
    is_resolved = Column(Boolean, default=False, nullable=False)
    resolved_by = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    processing_date_hour = Column(DateTime, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    metadata_manual_threshold = relationship("BatchTableMetadataManualThreshold", back_populates="results")
    batch_table_metadata = relationship("BatchTableMetadata", back_populates="batch_table_metadata_metrics_verify")
    resolved_by_user = relationship("User", foreign_keys=[resolved_by])

    __table_args__ = (
        Index("ix_batch_table_metadata_metrics_verify__threshold_batch_unique", "metadata_manual_threshold_id", "batch_table_metadata_id", unique=True),
        Index("ix_batch_table_metadata_metrics_verify__threshold_batch", "metadata_manual_threshold_id", "batch_table_metadata_id"),
        Index("ix_batch_table_metadata_metrics_verify__batch_status", "batch_table_metadata_id", "status"),
    )
