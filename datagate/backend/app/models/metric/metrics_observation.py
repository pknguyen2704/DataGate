MetricObservationfrom sqlalchemy import (
    Column,
    BigInteger,
    String,
    Float,
    DateTime,
    ForeignKey,
    JSON,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import now

from app.db.base import Base


class MetricObservation(Base):
    """
    Lưu giá trị thực tế của metric theo từng batch.

    Đây là bảng chuẩn hóa metric từ nhiều nguồn:
    - table_metadata
    - data_profile_metric
    - quality_rule_result
    - ml_experiment_run

    Prophet nên đọc dữ liệu lịch sử từ bảng này.
    Grafana cũng có thể đọc bảng này để vẽ actual values.
    """

    __tablename__ = "metric_observation"

    id = Column(BigInteger, primary_key=True, index=True)

    table_id = Column(
        BigInteger,
        ForeignKey("table.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Batch metadata nguồn
    source_metadata_id = Column(
        BigInteger,
        ForeignKey("table_metadata.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    metric_id = Column(
        BigInteger,
        ForeignKey("metric_definition.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Thời điểm metric xảy ra.
    # Nên dùng table_metadata.last_updated_time.
    metric_time = Column(DateTime(timezone=True), nullable=False, index=True)

    # TABLE, COLUMN, MODEL, RULE
    target_type = Column(String, nullable=False, default="TABLE")

    # Nếu target_type = TABLE thì dùng "__table__"
    # Nếu target_type = COLUMN thì là tên cột, ví dụ "fare_amount"
    # Nếu target_type = MODEL thì là tên model, ví dụ "xgboost"
    # Nếu target_type = RULE thì là rule name/id
    target_name = Column(String, nullable=False, default="__table__")

    # Giá trị thực tế của metric
    actual_value = Column(Float, nullable=True)

    # Nguồn gốc metric:
    # METADATA, PROFILING, RULE, ML
    source_type = Column(String, nullable=False)

    # Tên bảng nguồn nếu muốn trace mềm
    # Ví dụ: table_metadata, data_profile_metric, ml_experiment_run
    source_ref_table = Column(String, nullable=True)

    # ID record nguồn nếu muốn trace mềm
    source_ref_id = Column(BigInteger, nullable=True)

    raw_value = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, default=now())

    table = relationship(
        "Table",
        back_populates="metric_observations",
    )

    source_metadata = relationship(
        "TableMetadata",
        back_populates="metric_observations",
    )

    metric = relationship(
        "MetricDefinition",
        back_populates="observations",
    )

    evaluations = relationship(
        "MetricEvaluation",
        back_populates="observation",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint(
            "table_id",
            "source_metadata_id",
            "metric_id",
            "target_type",
            "target_name",
            name="uq_metric_observation_table_batch_metric_target",
        ),
        Index("idx_metric_observation_table_time", "table_id", "metric_time"),
        Index("idx_metric_observation_metric_time", "metric_id", "metric_time"),
        Index("idx_metric_observation_target", "target_type", "target_name"),
        Index("idx_metric_observation_source", "source_type", "source_ref_table", "source_ref_id"),
    )