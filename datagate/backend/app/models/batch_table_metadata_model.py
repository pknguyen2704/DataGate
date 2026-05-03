import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class BatchTableMetadata(Base):
    __tablename__ = "table_batch_metadata"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)

    table_id = Column(
        UUID(as_uuid=False),
        ForeignKey("tables.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    snapshot_id = Column(String(255), nullable=False, index=True)
    parent_snapshot_id = Column(String(255), nullable=True)

    operation = Column(String(50), nullable=True)
    last_updated_time = Column(DateTime, nullable=True)

    batch_added_rows = Column(BigInteger, nullable=True)
    batch_added_files = Column(Integer, nullable=True)

    deleted_rows = Column(BigInteger, nullable=True)
    deleted_files = Column(Integer, nullable=True)

    table_total_rows = Column(BigInteger, nullable=True)
    table_total_files = Column(Integer, nullable=True)
    table_total_size_bytes = Column(BigInteger, nullable=True)

    changed_partition_count = Column(Integer, nullable=True)

    schema_id = Column(Integer, nullable=True)
    latest_sequence_number = Column(BigInteger, nullable=True)

    metadata_recorded_at = Column(DateTime, nullable=True)

    collected_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    table = relationship(
        "Table",
        back_populates="batch_metadata",
    )

    __table_args__ = (
        UniqueConstraint(
            "table_id",
            "snapshot_id",
            name="uq_table_batch_metadata_table_snapshot",
        ),
    )