import uuid

from sqlalchemy import Column, DateTime, Float, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class AnomalyConfig(Base):
    __tablename__ = "anomaly_configs"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    table_id = Column(
        UUID(as_uuid=False),
        ForeignKey("tables.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    batch_time_col = Column(String(255), nullable=False)
    feature_config = Column(JSONB, nullable=False)
    model_parameters = Column(JSONB, nullable=False)
    column_config = Column(JSONB, nullable=False)
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

    table = relationship("Table", back_populates="anomaly_config")
    results = relationship(
        "AnomalyResult", back_populates="anomaly_config", cascade="all, delete-orphan"
    )
    created_by_user = relationship("User", foreign_keys=[created_by])
    last_modified_by_user = relationship("User", foreign_keys=[last_modified_by])

    __table_args__ = (Index("ix_anomaly_configs__table_id", "table_id", unique=True),)


class AnomalyResult(Base):
    __tablename__ = "anomaly_results"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    table_id = Column(
        UUID(as_uuid=False), ForeignKey("tables.id", ondelete="CASCADE"), nullable=False
    )
    anomaly_config_id = Column(
        UUID(as_uuid=False),
        ForeignKey("anomaly_configs.id", ondelete="CASCADE"),
        nullable=False,
    )

    processing_date_hour = Column(DateTime, nullable=False)
    auc_score = Column(Float, nullable=True)
    p_value = Column(Float, nullable=True)
    parameter_snapshot = Column(JSONB, nullable=True)
    feature_config_snapshot = Column(JSONB, nullable=True)
    shap_top_features = Column(JSONB, nullable=True)

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    table = relationship("Table", back_populates="anomaly_results")
    anomaly_config = relationship("AnomalyConfig", back_populates="results")
    quality_check_results = relationship(
        "QualityCheckResult", back_populates="anomaly_result"
    )

    __table_args__ = (
        Index(
            "ix_anomaly_results__table_hour",
            "table_id",
            "processing_date_hour",
            unique=True,
        ),
        Index(
            "ix_anomaly_results__config_hour",
            "anomaly_config_id",
            "processing_date_hour",
        ),
    )
