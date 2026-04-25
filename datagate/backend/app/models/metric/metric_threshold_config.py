from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import now

from app.db.base import Base


class MetricThresholdConfig(Base):
    """
    Lưu threshold thủ công do người dùng cấu hình.

    Nếu có threshold manual enabled thì evaluation dùng manual.
    Nếu không có thì dùng Prophet prediction.
    """

    __tablename__ = "metric_threshold_config"

    id = Column(BigInteger, primary_key=True, index=True)

    table_id = Column(
        BigInteger,
        ForeignKey("table.id", ondelete="CASCADE"),
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

    # "__table__", column_name, model_name, rule_name...
    target_name = Column(String, nullable=False, default="__table__")

    min_value = Column(Float, nullable=True)
    max_value = Column(Float, nullable=True)

    is_enabled = Column(Boolean, nullable=False, default=True)

    # low, medium, high, critical
    severity = Column(String, nullable=False, default="medium")

    created_by = Column(BigInteger, nullable=True)
    updated_by = Column(BigInteger, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, default=now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=now(), onupdate=now())

    table = relationship(
        "Table",
        back_populates="metric_threshold_configs",
    )

    metric = relationship(
        "MetricDefinition",
        back_populates="threshold_configs",
    )

    evaluations = relationship(
        "MetricEvaluation",
        back_populates="threshold_config",
    )

    __table_args__ = (
        UniqueConstraint(
            "table_id",
            "metric_id",
            "target_type",
            "target_name",
            name="uq_metric_threshold_config_table_metric_target",
        ),
        Index("idx_metric_threshold_config_enabled", "table_id", "is_enabled"),
        Index("idx_metric_threshold_config_target", "target_type", "target_name"),
    )