import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, UniqueConstraint
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
    numIterations = Column()
    earlyStoppingRound = Column()
    useBarrierExecutionMode = Column(Bool)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    shap_results = relationship(
        "SHAPResult",
        back_populates="lightgbm_parameter",
        cascade="all, delete-orphan",
    )

    table = relationship(
        "Table",
        back_populates="lightgbm_parameters",
    )

class LightGBMResult(Base):
    __tablename__ = "lightgbm_results"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)

    table_id = Column(
        UUID(as_uuid=False),
        ForeignKey("tables.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    lightgbm_parameter_id = Column(
        UUID(as_uuid=False),
        ForeignKey("lightgbm_parameters.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    processing_date_hour = Column(DateTime, nullable=False, index=True)

    auc_score = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    table = relationship(
        "Table",
        back_populates="lightgbm_results",
    )

    lightgbm_parameter = relationship(
        "LightGBMParameters",
        back_populates="results",
    )

    __table_args__ = (
        UniqueConstraint(
            "table_id",
            "lightgbm_parameter_id",
            "processing_date_hour",
            name="uq_lgbm_result_table_param_hour",
        ),
        Index(
            "ix_lgbm_result_table_param_hour",
            "table_id",
            "lightgbm_parameter_id",
            "processing_date_hour",
        ),
    )


def gen_uuid() -> str:
    return str(uuid.uuid4())


class SHAPResult(Base):
    __tablename__ = "shap_results"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)

    table_id = Column(
        UUID(as_uuid=False),
        ForeignKey("tables.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    lightgbm_parameter_id = Column(
        UUID(as_uuid=False),
        ForeignKey("lightgbm_parameters.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    processing_date_hour = Column(DateTime, nullable=False, index=True)
    feature_name = Column(String(255), nullable=False)
    shap_score = Column(Float, nullable=False)
    shap_rank = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    table = relationship(
        "Table",
        back_populates="shap_results",
    )

    lightgbm_parameter = relationship(
        "LightGBMParameters",
        back_populates="shap_results",
    )

    __table_args__ = (
        UniqueConstraint(
            "table_id",
            "lightgbm_parameter_id",
            "processing_date_hour",
            "feature_name",
            name="uq_shap_result_table_param_hour_feature",
        ),
        Index(
            "ix_shap_result_table_param_hour",
            "table_id",
            "lightgbm_parameter_id",
            "processing_date_hour",
        ),
        Index(
            "ix_shap_result_feature_name",
            "feature_name",
        ),
    )