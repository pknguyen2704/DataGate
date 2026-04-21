from sqlalchemy import Column, BigInteger, Text, DateTime, String
from sqlalchemy.sql.functions import now
from app.db.base import Base

class ObservabilityIncident(Base):
    __tablename__ = "observability_incidents"

    id = Column(BigInteger, primary_key=True, index=True)
    catalog = Column(Text, default="iceberg")
    schema_name = Column(Text)
    table_name = Column(Text)
    incident_type = Column(String) # drift, freshness, volume
    severity = Column(String) # low, medium, high
    message = Column(Text)
    status = Column(String, default="open") # open, resolved
    detected_at = Column(DateTime, default=now(), index=True) # Cột thời gian cho hypertable
    created_at = Column(DateTime, default=now())
