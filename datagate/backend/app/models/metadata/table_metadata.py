from sqlalchemy import (
    Column,
    BigInteger,
    String,
    DateTime,
    ForeignKey,
    JSON,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import now

from app.db.base import Base


class TableMetadata(Base):
    """
    Model lưu metadata cấp bảng theo từng batch/snapshot Iceberg.

    Bảng này phục vụ:
    - Freshness monitoring
    - Volume monitoring
    - Size monitoring
    - Prophet time-series anomaly detection

    Lưu ý:
    - Không dùng schema_id vì hệ thống hiện tại không thu thập được schema_id từ Iceberg.
    - Liên kết schema thông qua schema_version_id nội bộ.
    """

    __tablename__ = "table_metadata"

    id = Column(BigInteger, primary_key=True, index=True)

    table_id = Column(
        BigInteger,
        ForeignKey("table.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    snapshot_id = Column(BigInteger, nullable=False)
    parent_snapshot_id = Column(BigInteger, nullable=True)
    operation = Column(String, nullable=True)

    last_updated_time = Column(DateTime(timezone=True), nullable=False, index=True)
    collected_at = Column(DateTime(timezone=True), nullable=False, default=now(), index=True)

    batch_added_rows = Column(BigInteger, nullable=True)
    batch_added_files = Column(BigInteger, nullable=True)

    existing_rows = Column(BigInteger, nullable=True)
    existing_files = Column(BigInteger, nullable=True)

    deleted_rows = Column(BigInteger, nullable=True)
    deleted_files = Column(BigInteger, nullable=True)

    table_total_rows_after_commit = Column(BigInteger, nullable=True)
    table_total_files_after_commit = Column(BigInteger, nullable=True)
    table_total_size_bytes_after_commit = Column(BigInteger, nullable=True)

    current_file_count = Column(BigInteger, nullable=True)
    current_total_rows = Column(BigInteger, nullable=True)
    current_total_size_bytes = Column(BigInteger, nullable=True)

    changed_partition_count = Column(BigInteger, nullable=True)

    # FK tới schema version nội bộ của hệ thống
    schema_version_id = Column(
        BigInteger,
        ForeignKey("table_schema_version.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    raw_snapshot_summary = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, default=now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=now(), onupdate=now())

    table = relationship(
        "Table",
        back_populates="table_metadata",
    )

    schema_version = relationship(
        "TableSchemaVersion",
        back_populates="table_metadata",
    )

    __table_args__ = (
        UniqueConstraint(
            "table_id",
            "snapshot_id",
            name="uq_table_metadata_table_snapshot",
        ),
        Index("idx_table_metadata_table_time", "table_id", "collected_at"),
        Index("idx_table_metadata_table_last_updated", "table_id", "last_updated_time"),
        Index("idx_table_metadata_snapshot", "snapshot_id"),
        Index("idx_table_metadata_schema_version", "table_id", "schema_version_id"),
    )