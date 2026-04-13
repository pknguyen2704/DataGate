from sqlalchemy import Column, Integer, String, DateTime, BigInteger, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class ProfilingRun(Base):
    __tablename__ = "profiling_runs"

    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String)
    batch_time = Column(DateTime)
    partition_key = Column(String)
    num_records = Column(BigInteger)
    raw_json = Column(JSON)
    created_at = Column(DateTime)

    columns = relationship("ColumnProfile", back_populates="run")

class ColumnProfile(Base):
    __tablename__ = "column_profiles"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("profiling_runs.id"))
    column_name = Column(String)
    data_type = Column(String)
    
    completeness = Column(Float)
    approx_distinct = Column(BigInteger)
    
    mean = Column(Float)
    min = Column(Float)
    max = Column(Float)
    stddev = Column(Float)

    run = relationship("ProfilingRun", back_populates="columns")
