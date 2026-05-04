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

    # Phân loại metric:
    # - metadata: metric cấp bảng, ví dụ batch_added_rows, table_total_rows
    # - profiling: metric cấp cột, ví dụ mean, completeness, distinctness
    metric_group = Column(
        Enum(
            "metadata",
            "profiling",
            name="metric_manual_threshold_group",
        ),
        nullable=False,
        index=True,
    )

    # Với metadata/table-level metric, set column_name = "__table__"
    # Với profiling/column-level metric, set column_name = tên cột thật
    #
    # Ví dụ:
    # metadata  | __table__     | batch_added_rows
    # profiling | trip_distance | mean
    # profiling | passenger_cnt | completeness
    column_name = Column(String(255), nullable=False, default="__table__")

    # Tên metric cần đặt ngưỡng
    #
    # Metadata examples:
    # - batch_added_rows
    # - batch_added_files
    # - deleted_rows
    # - deleted_files
    # - table_total_rows
    # - table_total_files
    # - table_total_size_bytes
    #
    # Profiling examples:
    # - completeness
    # - mean
    # - standard_deviation
    # - minimum
    # - maximum
    # - min_length
    # - max_length
    # - distinctness
    # - approx_count_distinct
    metric_name = Column(String(255), nullable=False, index=True)

    # Nếu actual_value < min_threshold thì cảnh báo.
    # Nếu actual_value > max_threshold thì cảnh báo.
    #
    # Dùng Float để hỗ trợ cả metric dạng số nguyên và số thực.
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

    table_id = Column(
        UUID(as_uuid=False),
        ForeignKey("tables.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Với metric cấp bảng: column_name = "__table__"
    # Với metric profiling theo cột: column_name = tên cột thật
    column_name = Column(String(255), nullable=False, default="__table__")

    # Ví dụ:
    # batch_added_rows, table_total_rows, completeness, mean, distinctness
    metric_name = Column(String(255), nullable=False, index=True)

    status = Column(
        Enum(
            "pass",
            "fail",
            name="metric_result_status",
        ),
        nullable=False,
        index=True,
    )

    # Giá trị thực tế đo được tại batch đó
    actual_value = Column(Float, nullable=True)

    # Ngưỡng được dùng tại thời điểm kiểm tra
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

    message = Column(Text, nullable=True)

    processing_date_hour = Column(DateTime, nullable=False, index=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    table = relationship(
        "Table",
        back_populates="metric_results",
    )

    __table_args__ = (
        UniqueConstraint(
            "table_id",
            "column_name",
            "metric_name",
            "processing_date_hour",
            name="uq_metric_result_table_column_metric_hour",
        ),
        Index(
            "ix_metric_result_lookup",
            "table_id",
            "column_name",
            "metric_name",
            "processing_date_hour",
        ),
        Index(
            "ix_metric_result_status",
            "table_id",
            "status",
            "processing_date_hour",
        ),
    )