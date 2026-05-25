import uuid

from sqlalchemy import Column, DateTime, Float, ForeignKey, Index, Integer, String, Text, func
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
    )

    batch_time_col = Column(String(255), nullable=False)
    required_history_days = Column(Integer, nullable=False)
    previous_batch_hours = Column(Integer, nullable=False)
    history_days = Column(JSONB, nullable=False)
    target_sample_per_group = Column(Integer, nullable=False)
    test_size = Column(Float, nullable=False)
    random_state = Column(Integer, nullable=False)
    exclude_cols = Column(JSONB, nullable=False)
    categorical_cols = Column(JSONB, nullable=False)
    numeric_cols = Column(JSONB, nullable=False)
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
    created_by_user = relationship("User", foreign_keys=[created_by])
    last_modified_by_user = relationship("User", foreign_keys=[last_modified_by])

    __table_args__ = (Index("ix_anomaly_configs__table_id", "table_id", unique=True),)


class ModelParameter(Base):
    __tablename__ = "model_parameters"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    table_id = Column(
        UUID(as_uuid=False),
        ForeignKey("tables.id", ondelete="CASCADE"),
        nullable=False,
    )
    learning_rate = Column(Float, nullable=False)
    num_leaves = Column(Integer, nullable=False)
    max_depth = Column(Integer, nullable=False)
    min_data_in_leaf = Column(Integer, nullable=False)
    bagging_fraction = Column(Float, nullable=False)
    bagging_freq = Column(Integer, nullable=False)
    feature_fraction = Column(Float, nullable=False)
    lambda_l1 = Column(Float, nullable=False)
    lambda_l2 = Column(Float, nullable=False)
    min_gain_to_split = Column(Float, nullable=False)
    max_bin = Column(Integer, nullable=False)
    num_iterations = Column(Integer, nullable=False)
    created_by = Column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    last_modified_by = Column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    table = relationship("Table")
    results = relationship(
        "AnomalyResult", back_populates="model_parameter"
    )
    created_by_user = relationship("User", foreign_keys=[created_by])
    last_modified_by_user = relationship("User", foreign_keys=[last_modified_by])

    __table_args__ = (Index("ix_model_parameters__table_id", "table_id", unique=True),)




class AnomalyResult(Base):
    __tablename__ = "anomaly_results"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    table_id = Column(
        UUID(as_uuid=False), ForeignKey("tables.id", ondelete="CASCADE"), nullable=False
    )
    model_parameter_id = Column(
        UUID(as_uuid=False),
        ForeignKey("model_parameters.id", ondelete="SET NULL"),
        nullable=True,
    )

    processing_date_hour = Column(DateTime, nullable=False)
    auc_score = Column(Float, nullable=True)
    parameter_snapshot = Column(JSONB, nullable=True)
    config_snapshot = Column(JSONB, nullable=True)
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
    model_parameter = relationship("ModelParameter", back_populates="results")
    quality_check_results = relationship(
        "QualityCheckResult", back_populates="anomaly_result"
    )
    shap_results = relationship(
        "SHAPResult", back_populates="anomaly_result", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index(
            "ix_anomaly_results__table_hour",
            "table_id",
            "processing_date_hour",
            unique=True,
        ),
        Index(
            "ix_anomaly_results__param_hour",
            "model_parameter_id",
            "processing_date_hour",
        ),
    )


class SHAPResult(Base):
    __tablename__ = "shap_results"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    anomaly_result_id = Column(
        UUID(as_uuid=False),
        ForeignKey("anomaly_results.id", ondelete="CASCADE"),
        nullable=False,
    )
    feature_name = Column(String(255), nullable=False)
    shap_score = Column(Float, nullable=False)
    shap_rank = Column(Integer, nullable=False)
    processing_date_hour = Column(DateTime, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    anomaly_result = relationship("AnomalyResult", back_populates="shap_results")

    __table_args__ = (
        Index(
            "ix_shap_results__result_feature",
            "anomaly_result_id",
            "feature_name",
            unique=True,
        ),
    )
