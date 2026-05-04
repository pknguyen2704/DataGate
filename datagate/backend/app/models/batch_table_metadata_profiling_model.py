import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class BatchTableMetadata(Base):
    __tablename__ = "batch_table_metadata"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)

    table_id = Column(
        UUID(as_uuid=False),
        ForeignKey("tables.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    batch_added_rows = Column(BigInteger, nullable=True)
    batch_added_files = Column(Integer, nullable=True)
    table_total_rows = Column(BigInteger, nullable=True)
    table_total_files = Column(Integer, nullable=True)
    table_total_size_bytes = Column(BigInteger, nullable=True) 
    
    processing_date_hour = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    table = relationship(
        "Table",
        back_populates="batch_table_metadata",
    )
    
    __table_args__ = (
        UniqueConstraint(
            "table_id",
            "processing_date_hour",
            name="uq_batch_table_metadata_table_id_processing_date_hour",
        ),
    )

class BatchTableProfiling(Base):
    __tablename__ = "batch_table_profiling"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)

    table_id = Column(
        UUID(as_uuid=False),
        ForeignKey("tables.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    column_name = Column(String(255), nullable=False)
    data_type = Column(String(100), nullable=True)

    completeness = Column(Float, nullable=True)

    mean = Column(Float, nullable=True)
    standard_deviation = Column(Float, nullable=True)
    minimum = Column(Float, nullable=True)
    maximum = Column(Float, nullable=True)

    min_length = Column(Integer, nullable=True)
    max_length = Column(Integer, nullable=True)

    distinctness = Column(Float, nullable=True)
    approx_count_distinct = Column(BigInteger, nullable=True)

    processing_date_hour = Column(DateTime, nullable=False, index=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    table = relationship(
        "Table",
        back_populates="batch_table_profiling",
    )

    __table_args__ = (
        UniqueConstraint(
            "table_id",
            "processing_date_hour",
            "column_name",
            name="uq_batch_table_profiling_table_hour_column",
        ),
        Index(
            "ix_batch_table_profiling_lookup",
            "table_id",
            "column_name",
            "processing_date_hour",
        ),
    )