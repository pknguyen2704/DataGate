import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class ModelParameter(Base):
    __tablename__ = "model_parameters"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    table_id = Column(
        UUID(as_uuid=False), ForeignKey("tables.id", ondelete="CASCADE"), nullable=False
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

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    created_by = Column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    last_modified_by = Column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    table = relationship("Table", back_populates="model_parameter")
    results = relationship(
        "AUCResult", back_populates="model_parameter", cascade="all, delete-orphan"
    )
    manual_thresholds = relationship(
        "AUCManualThreshold",
        back_populates="model_parameter",
        cascade="all, delete-orphan",
    )
    created_by_user = relationship("User", foreign_keys=[created_by])
    last_modified_by_user = relationship("User", foreign_keys=[last_modified_by])

    __table_args__ = (Index("ix_model_parameters__table_id", "table_id", unique=True),)


class ModelConfig(Base):
    __tablename__ = "model_configs"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    table_id = Column(
        UUID(as_uuid=False), ForeignKey("tables.id", ondelete="CASCADE"), nullable=False
    )
    batch_time_col = Column(String(255), nullable=False)

    required_history_days = Column(Integer, nullable=False)
    previous_batch_hours = Column(Integer, nullable=False)
    history_days = Column(JSONB, nullable=False)
    target_sample_per_group = Column(Integer, nullable=False)
    test_size = Column(Float, nullable=False)
    random_state = Column(Integer, nullable=False)
    p_value_alpha = Column(Float, nullable=False)
    min_history_auc_points = Column(Integer, nullable=False)
    exclude_cols = Column(JSONB, default=list, nullable=False)
    categorical_cols = Column(JSONB, default=list, nullable=False)
    numeric_cols = Column(JSONB, default=list, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    created_by = Column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    last_modified_by = Column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    table = relationship("Table", back_populates="model_config")
    created_by_user = relationship("User", foreign_keys=[created_by])
    last_modified_by_user = relationship("User", foreign_keys=[last_modified_by])

    __table_args__ = (Index("ix_model_configs__table_id", "table_id", unique=True),)


class AUCResult(Base):
    __tablename__ = "auc_results"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    table_id = Column(
        UUID(as_uuid=False), ForeignKey("tables.id", ondelete="CASCADE"), nullable=False
    )
    model_parameter_id = Column(
        UUID(as_uuid=False),
        ForeignKey("model_parameters.id", ondelete="RESTRICT"),
        nullable=False,
    )

    processing_date_hour = Column(DateTime, nullable=False)

    auc_score = Column(Float, nullable=True)
    p_value = Column(Float, nullable=True)
    parameter_snapshot = Column(JSONB, nullable=True)
    feature_config_snapshot = Column(JSONB, nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    table = relationship("Table", back_populates="auc_results")
    model_parameter = relationship("ModelParameter", back_populates="results")
    shap_results = relationship(
        "SHAPResult", back_populates="auc_result", cascade="all, delete-orphan"
    )
    auc_verify = relationship(
        "AUCVerify",
        back_populates="auc_result",
        uselist=False,
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index(
            "ix_auc_results__table_hour_unique",
            "table_id",
            "processing_date_hour",
            unique=True,
        ),
        Index(
            "ix_auc_results__param_hour", "model_parameter_id", "processing_date_hour"
        ),
        Index("ix_auc_results__table_hour", "table_id", "processing_date_hour"),
    )


class SHAPResult(Base):
    __tablename__ = "shap_results"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    auc_result_id = Column(
        UUID(as_uuid=False),
        ForeignKey("auc_results.id", ondelete="CASCADE"),
        nullable=False,
    )

    feature_name = Column(String(255), nullable=False)
    shap_score = Column(Float, nullable=False)
    shap_rank = Column(Integer, nullable=False)
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

    auc_result = relationship("AUCResult", back_populates="shap_results")

    __table_args__ = (
        Index(
            "ix_shap_results__result_feature",
            "auc_result_id",
            "feature_name",
            unique=True,
        ),
        Index("ix_shap_results__auc_result_rank", "auc_result_id", "shap_rank"),
    )


class AUCManualThreshold(Base):
    __tablename__ = "auc_manual_thresholds"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    model_parameter_id = Column(
        UUID(as_uuid=False),
        ForeignKey("model_parameters.id", ondelete="CASCADE"),
        nullable=False,
    )

    auc_threshold = Column(Float, nullable=False)
    severity_level = Column(
        Enum("warning", "critical", name="manual_threshold_severity_level"),
        nullable=False,
    )
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    created_by = Column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    last_modified_by = Column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    created_by_user = relationship("User", foreign_keys=[created_by])
    last_modified_by_user = relationship("User", foreign_keys=[last_modified_by])
    model_parameter = relationship("ModelParameter", back_populates="manual_thresholds")
    auc_verifies = relationship("AUCVerify", back_populates="manual_threshold")


class AUCVerify(Base):
    __tablename__ = "auc_verify"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    auc_result_id = Column(
        UUID(as_uuid=False),
        ForeignKey("auc_results.id", ondelete="CASCADE"),
        nullable=False,
    )
    manual_threshold_id = Column(
        UUID(as_uuid=False),
        ForeignKey("auc_manual_thresholds.id", ondelete="SET NULL"),
        nullable=True,
    )

    status = Column(Enum("pass", "fail", name="model_verify_status"), nullable=False)
    auc_score = Column(Float, nullable=True)
    auc_threshold = Column(Float, nullable=True)
    severity_level = Column(
        Enum("warning", "critical", name="manual_threshold_severity_level"),
        nullable=True,
    )
    is_resolved = Column(Boolean, default=False, nullable=False)
    resolved_by = Column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
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

    auc_result = relationship("AUCResult", back_populates="auc_verify")
    manual_threshold = relationship("AUCManualThreshold", back_populates="auc_verifies")
    resolved_by_user = relationship("User", foreign_keys=[resolved_by])

    __table_args__ = (
        Index("ix_auc_verify__auc_result_id", "auc_result_id", unique=True),
        Index("ix_auc_verify__status", "status"),
    )
