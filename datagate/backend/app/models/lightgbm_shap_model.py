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
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class LightGBMParameter(Base):
    __tablename__ = "lightgbm_parameters"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)

    table_id = Column(
        UUID(as_uuid=False),
        ForeignKey("tables.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Tunable params
    learningRate = Column(Float, default=0.05, nullable=False)
    numLeaves = Column(Integer, default=31, nullable=False)
    maxDepth = Column(Integer, default=-1, nullable=False)
    minDataInLeaf = Column(Integer, default=20, nullable=False)

    baggingFraction = Column(Float, default=1.0, nullable=False)
    baggingFreq = Column(Integer, default=0, nullable=False)
    featureFraction = Column(Float, default=1.0, nullable=False)

    lambdaL1 = Column(Float, default=1e-8, nullable=False)
    lambdaL2 = Column(Float, default=1e-8, nullable=False)
    minGainToSplit = Column(Float, default=0.0, nullable=False)
    maxBin = Column(Integer, default=255, nullable=False)

    # Runtime params
    numIterations = Column(Integer, default=300, nullable=False)
    earlyStoppingRound = Column(Integer, default=30, nullable=False)
    useBarrierExecutionMode = Column(Boolean, default=True, nullable=False)

    # Job sẽ lấy parameter active của từng table để chạy
    is_active = Column(Boolean, default=True, nullable=False, index=True)

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
        back_populates="lightgbm_parameters",
    )

    manual_thresholds = relationship(
        "LightGBMManualThreshold",
        back_populates="lightgbm_parameter",
        cascade="all, delete-orphan",
    )

    results = relationship(
        "LightGBMResult",
        back_populates="lightgbm_parameter",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index(
            "ix_lgbm_param_table_active",
            "table_id",
            "is_active",
        ),

        # Mỗi table chỉ nên có 1 bộ parameter active.
        Index(
            "uq_lgbm_param_one_active_per_table",
            "table_id",
            unique=True,
            postgresql_where=text("is_active = true"),
        ),
    )


class LightGBMManualThreshold(Base):
    __tablename__ = "lightgbm_manual_thresholds"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)

    lightgbm_parameter_id = Column(
        UUID(as_uuid=False),
        ForeignKey("lightgbm_parameters.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Với AUC drift detection, thường dùng auc_max_threshold.
    # Ví dụ auc_score > 0.70 => fail.
    auc_min_threshold = Column(Float, nullable=True)
    auc_max_threshold = Column(Float, nullable=True)

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

    is_active = Column(Boolean, default=True, nullable=False, index=True)

    description = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    lightgbm_parameter = relationship(
        "LightGBMParameter",
        back_populates="manual_thresholds",
    )

    results = relationship(
        "LightGBMResult",
        back_populates="manual_threshold",
    )

    __table_args__ = (
        Index(
            "ix_lgbm_manual_threshold_param_active",
            "lightgbm_parameter_id",
            "is_active",
        ),

        # Mỗi parameter chỉ nên có 1 threshold active.
        Index(
            "uq_lgbm_manual_threshold_one_active_per_param",
            "lightgbm_parameter_id",
            unique=True,
            postgresql_where=text("is_active = true"),
        ),
    )


class LightGBMResult(Base):
    __tablename__ = "lightgbm_results"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)

    lightgbm_parameter_id = Column(
        UUID(as_uuid=False),
        ForeignKey("lightgbm_parameters.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    manual_threshold_id = Column(
        UUID(as_uuid=False),
        ForeignKey("lightgbm_manual_thresholds.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    processing_date_hour = Column(DateTime, nullable=False, index=True)

    auc_score = Column(Float, nullable=True)

    status = Column(
        Enum(
            "pass",
            "fail",
            "not_checked",
            name="lightgbm_result_status",
        ),
        nullable=False,
        default="not_checked",
        index=True,
    )

    # Snapshot threshold tại thời điểm chạy.
    # Nếu user sửa threshold sau này, lịch sử vẫn giữ đúng ngưỡng đã dùng.
    auc_min_threshold = Column(Float, nullable=True)
    auc_max_threshold = Column(Float, nullable=True)

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

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    lightgbm_parameter = relationship(
        "LightGBMParameter",
        back_populates="results",
    )

    manual_threshold = relationship(
        "LightGBMManualThreshold",
        back_populates="results",
    )

    shap_results = relationship(
        "SHAPResult",
        back_populates="lightgbm_result",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint(
            "lightgbm_parameter_id",
            "processing_date_hour",
            name="uq_lgbm_result_param_hour",
        ),
        Index(
            "ix_lgbm_result_param_hour",
            "lightgbm_parameter_id",
            "processing_date_hour",
        ),
        Index(
            "ix_lgbm_result_status_hour",
            "status",
            "processing_date_hour",
        ),
    )


class SHAPResult(Base):
    __tablename__ = "shap_results"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)

    lightgbm_result_id = Column(
        UUID(as_uuid=False),
        ForeignKey("lightgbm_results.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    feature_name = Column(String(255), nullable=False)
    shap_score = Column(Float, nullable=False)
    shap_rank = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    lightgbm_result = relationship(
        "LightGBMResult",
        back_populates="shap_results",
    )

    __table_args__ = (
        UniqueConstraint(
            "lightgbm_result_id",
            "feature_name",
            name="uq_shap_result_lgbm_result_feature",
        ),
        Index(
            "ix_shap_result_lgbm_result_rank",
            "lightgbm_result_id",
            "shap_rank",
        ),
        Index(
            "ix_shap_result_feature_name",
            "feature_name",
        ),
    )