from sqlalchemy import Column, BigInteger, Text, DateTime
from sqlalchemy.sql.functions import now
from app.db.base import Base

class ObservabilitySnapshot(Base):
    __tablename__ = "observability_snapshots"

    # Lưu ý: Với TimescaleDB, PK nên bao gồm cột thời gian nếu muốn đảm bảo tính duy nhất
    id = Column(BigInteger, primary_key=True, index=True)
    catalog = Column(Text, default="iceberg")
    schema_name = Column(Text)
    table_name = Column(Text)
    snapshot_time = Column(DateTime, index=True) # Cột thời gian cho hypertable
    last_updated_time = Column(DateTime)
    total_records = Column(BigInteger)
    total_size = Column(BigInteger)
    created_at = Column(DateTime, default=now())
