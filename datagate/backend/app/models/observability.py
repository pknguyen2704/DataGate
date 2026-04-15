from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, BigInteger, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import now
from app.db.base_class import Base

class DQJobConfig(Base):
    __tablename__ = "dq_job_config"

    id = Column(Integer, primary_key=True, index=True)
    catalog = Column(Text)
    schema_name = Column(Text)
    table_name = Column(Text)
    hour = Column(Integer, nullable=True)
    minute = Column(Integer, nullable=True)
    schedule_type = Column(Text, default="daily")
    interval_minutes = Column(Integer, nullable=True)
    dag_id = Column(Text, default="dq_metadata_collector")
    job_type = Column(Text, default="metadata_profile")
    is_active = Column(Boolean, default=True)
    last_run_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=now())

class DQJobRunHistory(Base):
    __tablename__ = "dq_job_run_history"

    id = Column(BigInteger, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("dq_job_config.id"), nullable=False)
    dag_id = Column(Text)
    dag_run_id = Column(Text)
    trigger_type = Column(Text, default="scheduled")
    status = Column(Text, default="queued")
    scheduled_for = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=now())

    job = relationship("DQJobConfig")

class DQTableSnapshot(Base):
    __tablename__ = "dq_table_snapshot"

    id = Column(BigInteger, primary_key=True, index=True)
    table_name = Column(Text)
    snapshot_time = Column(DateTime)
    last_updated_time = Column(DateTime) # Freshness
    total_records = Column(BigInteger) # Volume
    total_size = Column(BigInteger)
    created_at = Column(DateTime, default=now())

class DQTableVolumeTS(Base):
    __tablename__ = "dq_table_volume_ts"

    id = Column(BigInteger, primary_key=True, index=True)
    table_name = Column(Text)
    dt = Column(Date)
    records_added = Column(BigInteger)
    created_at = Column(DateTime, default=now())

class DQTableSchema(Base):
    __tablename__ = "dq_table_schema"

    id = Column(BigInteger, primary_key=True, index=True)
    table_name = Column(Text)
    column_name = Column(Text)
    data_type = Column(Text)
    snapshot_time = Column(DateTime)
    created_at = Column(DateTime, default=now())

class DQColumnStats(Base):
    __tablename__ = "dq_column_stats"

    id = Column(BigInteger, primary_key=True, index=True)
    table_name = Column(Text)
    column_name = Column(Text)
    nulls = Column(BigInteger)
    total = Column(BigInteger)
    snapshot_time = Column(DateTime)
    created_at = Column(DateTime, default=now())

class DQIncident(Base):
    __tablename__ = "dq_incidents"

    id = Column(BigInteger, primary_key=True, index=True)
    table_name = Column(Text)
    incident_type = Column(String) # drift, freshness, volume
    severity = Column(String) # low, medium, high
    message = Column(Text)
    status = Column(String, default="open") # open, resolved
    detected_at = Column(DateTime, default=now())
    created_at = Column(DateTime, default=now())
