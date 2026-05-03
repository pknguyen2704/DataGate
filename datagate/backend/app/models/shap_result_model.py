import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


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