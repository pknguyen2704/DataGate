from sqlalchemy import Column, BigInteger, Text, DateTime
from sqlalchemy.sql.functions import now
from app.db.base import Base

class ObservabilityVolumeTS(Base):
    __tablename__ = "observability_volume_ts"

    id = Column(BigInteger, primary_key=True, index=True)
    catalog = Column(Text, default="iceberg")
    schema_name = Column(Text)
    table_name = Column(Text)
    dt = Column(DateTime, index=True) # Cột thời gian cho hypertable
    records_added = Column(BigInteger)
    created_at = Column(DateTime, default=now())
