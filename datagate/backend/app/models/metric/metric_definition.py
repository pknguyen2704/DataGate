from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Text,
    Boolean,
    DateTime,
    Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import now

from app.db.base import Base


class MetricDefinition(Base):
    """
    Định nghĩa các metric hệ thống cần monitor.

    Ví dụ:
    - batch_added_rows
    - current_total_size_bytes
    - null_ratio
    - completeness
    - xgboost_auc

    Bảng này không lưu threshold.
    Threshold được lưu ở metric_threshold_config hoặc metric_prediction.
    """

    __tablename__ = "metric_definition"

    id = Column(BigInteger, primary_key=True, index=True)

    # Tên kỹ thuật dùng trong backend
    metric_name = Column(String, nullable=False, unique=True, index=True)

    # Tên hiển thị trên UI/Grafana
    display_name = Column(String, nullable=False)

    description = Column(Text, nullable=True)

    # Nhóm metric:
    # METADATA, PROFILING, RULE, ML
    metric_group = Column(String, nullable=False)

    # Nguồn sinh metric:
    # table_metadata, data_profile_metric, quality_rule_result, ml_experiment_run
    source_type = Column(String, nullable=False)

    # TABLE, COLUMN, MODEL, RULE
    default_target_type = Column(String, nullable=False, default="TABLE")

    # rows, files, bytes, ratio, score, percent
    unit = Column(String, nullable=True)

    # Có cho Prophet tự dự đoán threshold metric này không
    is_prophet_enabled = Column(Boolean, nullable=False, default=True)

    is_active = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime(timezone=True), nullable=False, default=now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=now(), onupdate=now())

    observations = relationship(
        "MetricObservation",
        back_populates="metric",
        cascade="all, delete-orphan",
    )

    threshold_configs = relationship(
        "MetricThresholdConfig",
        back_populates="metric",
        cascade="all, delete-orphan",
    )

    predictions = relationship(
        "MetricPrediction",
        back_populates="metric",
        cascade="all, delete-orphan",
    )

    evaluations = relationship(
        "MetricEvaluation",
        back_populates="metric",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("idx_metric_definition_group", "metric_group"),
        Index("idx_metric_definition_source", "source_type"),
        Index("idx_metric_definition_active", "is_active"),
    )