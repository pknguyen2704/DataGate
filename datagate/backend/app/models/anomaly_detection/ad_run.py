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


class ADRun(Base):
    """
    Lưu một lần chạy ML/Anomaly Detection.

    Ví dụ:
    - XGBoost + SHAP chạy sau batch metadata/profiling/rule
    - Lưu AUC, accuracy, precision, recall, f1_score
    """

    __tablename__ = "ad_run"

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
        nullable=True,
        index=True,
    )

    snapshot_id = Column(BigInteger, nullable=True, index=True)

    model_name = Column(String, nullable=False, default="xgboost")
    model_version = Column(String, nullable=True)

    run_type = Column(String, nullable=False, default="anomaly_detection")

    auc_score = Column(Float, nullable=True)
    accuracy = Column(Float, nullable=True)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)

    status = Column(String, nullable=False, default="SUCCESS")
    error_message = Column(String, nullable=True)

    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)

    model_params = Column(JSON, nullable=True)
    metrics_json = Column(JSON, nullable=True)

    artifact_path = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, default=now())

    table = relationship(
        "Table",
        back_populates="ad_runs",
    )

    source_metadata = relationship(
        "TableMetadata",
        back_populates="ad_runs",
    )

    feature_importances = relationship(
        "FeatureImportance",
        back_populates="ad_run",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("idx_ad_run_table_time", "table_id", "finished_at"),
        Index("idx_ad_run_metadata", "source_metadata_id"),
        Index("idx_ad_run_snapshot", "snapshot_id"),
        Index("idx_ad_run_model", "model_name", "model_version"),
        Index("idx_ad_run_status", "status"),
    )