from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Float,
    DateTime,
    ForeignKey,
    JSON,
    Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import now

from app.db.base import Base


class FeatureImportance(Base):
    """
    Lưu feature importance hoặc SHAP value từ AD/XGBoost run.

    Bảng này chủ yếu phục vụ UI explainability.
    Không bắt buộc phải đưa vào metric_observation.
    """

    __tablename__ = "feature_importance"

    id = Column(BigInteger, primary_key=True, index=True)

    ad_run_id = Column(
        BigInteger,
        ForeignKey("ad_run.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    feature_name = Column(String, nullable=False)

    importance_value = Column(Float, nullable=True)

    shap_value = Column(Float, nullable=True)

    rank = Column(BigInteger, nullable=True)

    extra_detail = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, default=now())

    ad_run = relationship(
        "ADRun",
        back_populates="feature_importances",
    )

    __table_args__ = (
        Index("idx_feature_importance_run_rank", "ad_run_id", "rank"),
        Index("idx_feature_importance_feature", "feature_name"),
    )