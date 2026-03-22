from sqlalchemy import Column, Integer, String, BigInteger, Float, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class ProfileRun(Base):
    __tablename__ = "profile_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    catalog = Column(Text, nullable=False)
    namespace = Column(Text, nullable=False)
    table_name = Column(Text, nullable=False, index=True)
    num_records = Column(BigInteger)
    raw_json = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship: 1 run -> many columns
    columns = relationship("ColumnProfile", back_populates="run", cascade="all, delete-orphan")

class ColumnProfile(Base):
    __tablename__ = "column_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("profile_runs.id", ondelete="CASCADE"))
    column_name = Column(Text, nullable=False)
    data_type = Column(Text)
    completeness = Column(Float)
    approx_distinct_values = Column(BigInteger)
    mean = Column(Float)
    maximum = Column(Float)
    minimum = Column(Float)
    sum = Column(Float)
    std_dev = Column(Float)
    
    run = relationship("ProfileRun", back_populates="columns")
    # Relationship: 1 column -> many histograms
    histograms = relationship("ColumnHistogram", back_populates="profile", cascade="all, delete-orphan")

class ColumnHistogram(Base):
    __tablename__ = "column_histograms"
    
    id = Column(Integer, primary_key=True, index=True)
    column_profile_id = Column(Integer, ForeignKey("column_profiles.id", ondelete="CASCADE"))
    bin_value = Column(Text)
    absolute_count = Column(BigInteger)
    ratio = Column(Float)
    
    profile = relationship("ColumnProfile", back_populates="histograms")
