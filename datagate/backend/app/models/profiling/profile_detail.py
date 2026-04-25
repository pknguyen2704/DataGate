from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Float,
    DateTime,
    ForeignKey,
    JSON,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import now

from app.db.base import Base


class ProfileDetail(Base):
    """
    Lưu chi tiết metric profiling trong một lần profile_run.

    Một dòng tương ứng với một metric profiling:
    - column_name = fare_amount
    - metric_name = null_ratio
    - metric_value = 0.002

    Nếu metric cấp bảng, column_name có thể NULL hoặc '__table__'.
    """

    __tablename__ = "profile_detail"

    id = Column(BigInteger, primary_key=True, index=True)

    profile_run_id = Column(
        BigInteger,
        ForeignKey("profile_run.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

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

    metric_time = Column(DateTime(timezone=True), nullable=False, index=True)

    column_name = Column(String, nullable=True)

    metric_name = Column(String, nullable=False)

    metric_value = Column(Float, nullable=True)

    metric_unit = Column(String, nullable=True)

    raw_value = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, default=now())

    profile_run = relationship(
        "ProfileRun",
        back_populates="details",
    )

    table = relationship(
        "Table",
        back_populates="profile_details",
    )

    source_metadata = relationship(
        "TableMetadata",
        back_populates="profile_details",
    )

    __table_args__ = (
        UniqueConstraint(
            "profile_run_id",
            "column_name",
            "metric_name",
            name="uq_profile_detail_run_column_metric",
        ),
        Index("idx_profile_detail_table_time", "table_id", "metric_time"),
        Index("idx_profile_detail_column_metric", "column_name", "metric_name"),
        Index("idx_profile_detail_metric_time", "metric_name", "metric_time"),
    )