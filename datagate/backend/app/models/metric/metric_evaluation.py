from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Float,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import now

from app.db.base import Base


class MetricPrediction(Base):
    """
    Lưu kết quả Prophet prediction.

    Một record tương ứng với:
    - một table
    - một metric
    - một target
    - một batch hiện tại cần evaluate
    """

    __tablename__ = "metric_prediction"

    id = Column(BigInteger, primary_key=True, index=True)

    table_id = Column(
        BigInteger,
        ForeignKey("table.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

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

    # TABLE, COLUMN, MODEL, RULE
    target_type = Column(String, nullable=False, default="TABLE")
    target_name = Column(String, nullable=False, default="__table__")

    # Thời điểm Prophet dự đoán cho metric này
    prediction_time = Column(DateTime(timezone=True), nullable=False, index=True)

    # Prophet yhat
    expected_value = Column(Float, nullable=True)

    # Prophet yhat_lower
    lower_bound = Column(Float, nullable=True)

    # Prophet yhat_upper
    upper_bound = Column(Float, nullable=True)

    model_name = Column(String, nullable=False, default="prophet")
    model_version = Column(String, nullable=True)

    training_window_start = Column(DateTime(timezone=True), nullable=True)
    training_window_end = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, default=now())

    table = relationship(
        "Table",
        back_populates="metric_predictions",
    )

    source_metadata = relationship(
        "TableMetadata",
        back_populates="metric_predictions",
    )

    metric = relationship(
        "MetricDefinition",
        back_populates="predictions",
    )

    evaluations = relationship(
        "MetricEvaluation",
        back_populates="prediction",
    )

    __table_args__ = (
        UniqueConstraint(
            "table_id",
            "source_metadata_id",
            "metric_id",
            "target_type",
            "target_name",
            "model_name",
            name="uq_metric_prediction_table_batch_metric_target_model",
        ),
        Index("idx_metric_prediction_table_time", "table_id", "prediction_time"),
        Index("idx_metric_prediction_metric_time", "metric_id", "prediction_time"),
        Index("idx_metric_prediction_target", "target_type", "target_name"),
    )