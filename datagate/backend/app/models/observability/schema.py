from sqlalchemy import Column, BigInteger, Text, DateTime
from sqlalchemy.sql.functions import now
from app.db.base import Base

class ObservabilitySchema(Base):
    __tablename__ = "observability_schema"

    id = Column(BigInteger, primary_key=True, index=True)
    catalog = Column(Text, default="iceberg")
    schema_name = Column(Text)
    table_name = Column(Text)
    column_name = Column(Text)
    data_type = Column(Text)
    snapshot_time = Column(DateTime, index=True)
    created_at = Column(DateTime, default=now())
