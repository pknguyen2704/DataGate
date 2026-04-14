from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import now
from app.db.base_class import Base

class QualityCheckRun(Base):
    __tablename__ = "quality_check_runs"

    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String)
    batch_time = Column(DateTime, default=now())
    partition_key = Column(String)
    total_checks = Column(Integer)
    failed_checks = Column(Integer)
    status = Column(String) # SUCCESS, FAILURE, WARNING

    results = relationship("QualityCheckResult", back_populates="run", cascade="all, delete-orphan")

class QualityCheckResult(Base):
    __tablename__ = "quality_check_results"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("quality_check_runs.id"))
    column_name = Column(String)
    rule_type = Column(String)
    constraint_status = Column(String) # Success, Failure
    constraint_message = Column(Text)
    severity = Column(String) # Error, Warning

    run = relationship("QualityCheckRun", back_populates="results")

class MLAnomalyRun(Base):
    __tablename__ = "ml_anomaly_runs"

    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String)
    batch_time = Column(DateTime, default=now())
    partition_key = Column(String)
    anomaly_score = Column(Float) # AUC score from binary classifier
    status = Column(String) # PASS, ALERT (if score > threshold)
    
    features = relationship("MLFeatureImportance", back_populates="run", cascade="all, delete-orphan")

class MLFeatureImportance(Base):
    __tablename__ = "ml_feature_importance"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("ml_anomaly_runs.id"))
    column_name = Column(String)
    importance_score = Column(Float)

    run = relationship("MLAnomalyRun", back_populates="features")
