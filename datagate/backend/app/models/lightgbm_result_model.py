import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


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