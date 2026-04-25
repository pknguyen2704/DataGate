from sqlalchemy import (
    Column,
    BigInteger,
    String,
    DateTime,
    ForeignKey,
    JSON,
    Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import now

from app.db.base import Base


class ProfileRun(Base):
    """
    Lưu lịch sử một lần chạy profiling cho một bảng.

    Một profile_run đại diện cho một profiling job sau một batch ingestion.
    Ví dụ:
    - profile bảng bronze.yellow_tripdata sau snapshot 12345
    - engine: deequ/custom_spark
    - status: SUCCESS/FAILED
    """

    __tablename__ = "profile_run"

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

    profiling_engine = Column(String, nullable=False, default="deequ")

    status = Column(String, nullable=False, default="SUCCESS")
    error_message = Column(String, nullable=True)

    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)

    raw_result = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, default=now())

    table = relationship(
        "Table",
        back_populates="profile_runs",
    )

    source_metadata = relationship(
        "TableMetadata",
        back_populates="profile_runs",
    )

    details = relationship(
        "ProfileDetail",
        back_populates="profile_run",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("idx_profile_run_table_time", "table_id", "finished_at"),
        Index("idx_profile_run_metadata", "source_metadata_id"),
        Index("idx_profile_run_snapshot", "snapshot_id"),
        Index("idx_profile_run_status", "status"),
    )