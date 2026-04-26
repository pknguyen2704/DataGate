"""
SQLAlchemy ORM Models — Metadata, Profiling, Rules, Quality, Thresholds, Anomaly, Alerts, Jobs
"""
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Boolean, DateTime, ForeignKey, Text,
    Enum, Integer, Float, BigInteger
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.base import Base


def gen_uuid():
    return str(uuid.uuid4())


# ─── Metadata ───────────────────────────────────────────────────────────────

class TableBatchMetadata(Base):
    __tablename__ = "table_batch_metadata"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    table_id = Column(UUID(as_uuid=False), ForeignKey("table_info.id", ondelete="CASCADE"), nullable=False, index=True)
    snapshot_id = Column(String(255), nullable=False, index=True)
    parent_snapshot_id = Column(String(255), nullable=True)
    batch_date_hour = Column(String(20), nullable=True)  # "2024-01-15-12"
    committed_at = Column(DateTime, nullable=True)
    operation = Column(String(50), nullable=True)  # append/overwrite/delete
    added_records = Column(BigInteger, nullable=True)
    added_files = Column(Integer, nullable=True)
    added_data_files_size = Column(BigInteger, nullable=True)
    total_records = Column(BigInteger, nullable=True)
    total_files = Column(Integer, nullable=True)
    collected_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    table = relationship("TableInfo")


class TableSchemaMetadata(Base):
    __tablename__ = "table_schema_metadata"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    table_id = Column(UUID(as_uuid=False), ForeignKey("table_info.id", ondelete="CASCADE"), nullable=False, index=True)
    snapshot_id = Column(String(255), nullable=False)
    column_name = Column(String(255), nullable=False)
    data_type = Column(String(100), nullable=True)
    nullable = Column(Boolean, nullable=True)
    ordinal_position = Column(Integer, nullable=True)
    collected_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    table = relationship("TableInfo")


class SchemaChangeEvent(Base):
    __tablename__ = "schema_change_events"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    table_id = Column(UUID(as_uuid=False), ForeignKey("table_info.id", ondelete="CASCADE"), nullable=False, index=True)
    snapshot_id = Column(String(255), nullable=True)
    change_type = Column(
        Enum("added", "removed", "type_changed", name="schema_change_type"),
        nullable=False
    )
    column_name = Column(String(255), nullable=False)
    old_type = Column(String(100), nullable=True)
    new_type = Column(String(100), nullable=True)
    detected_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    table = relationship("TableInfo")


# ─── Profiling ───────────────────────────────────────────────────────────────

class ColumnProfileMetric(Base):
    __tablename__ = "column_profile_metrics"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    table_id = Column(UUID(as_uuid=False), ForeignKey("table_info.id", ondelete="CASCADE"), nullable=False, index=True)
    snapshot_id = Column(String(255), nullable=False, index=True)
    batch_date_hour = Column(String(20), nullable=True)
    column_name = Column(String(255), nullable=False)
    data_type = Column(String(100), nullable=True)
    metric_name = Column(String(100), nullable=False)  # min, max, mean, completeness, ...
    metric_value = Column(Float, nullable=True)
    collected_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    table = relationship("TableInfo")


# ─── Rules ───────────────────────────────────────────────────────────────────

class QualityRule(Base):
    __tablename__ = "quality_rules"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    table_id = Column(UUID(as_uuid=False), ForeignKey("table_info.id", ondelete="CASCADE"), nullable=False, index=True)
    column_name = Column(String(255), nullable=True)  # nullable for table-level rules
    rule_name = Column(String(255), nullable=False)
    rule_type = Column(String(100), nullable=False)  # completeness, value_range, uniqueness, allowed_values, regex_pattern
    rule_config = Column(JSONB, nullable=False, default={})
    source = Column(
        Enum("system_suggested", "manual", name="rule_source"),
        nullable=False,
        default="manual"
    )
    status = Column(
        Enum("suggested", "enabled", "disabled", "rejected", name="rule_status"),
        nullable=False,
        default="suggested"
    )
    severity = Column(
        Enum("low", "medium", "high", "critical", name="rule_severity"),
        nullable=False,
        default="medium"
    )
    created_by = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_by = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    table = relationship("TableInfo")
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])
    validation_results = relationship("RuleValidationResult", back_populates="rule", lazy="dynamic")


# ─── Validation ──────────────────────────────────────────────────────────────

class RuleValidationRun(Base):
    __tablename__ = "rule_validation_runs"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    table_id = Column(UUID(as_uuid=False), ForeignKey("table_info.id", ondelete="CASCADE"), nullable=False, index=True)
    snapshot_id = Column(String(255), nullable=True)
    batch_date_hour = Column(String(20), nullable=True)
    status = Column(
        Enum("passed", "failed", "warning", "error", name="validation_status"),
        nullable=False,
        default="passed"
    )
    total_rules = Column(Integer, default=0)
    passed_rules = Column(Integer, default=0)
    failed_rules = Column(Integer, default=0)
    warning_rules = Column(Integer, default=0)
    anomaly_status = Column(String(50), nullable=True)
    auc_score = Column(Float, nullable=True)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    table = relationship("TableInfo")
    results = relationship("RuleValidationResult", back_populates="run", lazy="selectin")


class RuleValidationResult(Base):
    __tablename__ = "rule_validation_results"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    validation_run_id = Column(UUID(as_uuid=False), ForeignKey("rule_validation_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    rule_id = Column(UUID(as_uuid=False), ForeignKey("quality_rules.id", ondelete="SET NULL"), nullable=True)
    rule_name = Column(String(255), nullable=False)
    rule_type = Column(String(100), nullable=False)
    column_name = Column(String(255), nullable=True)
    status = Column(
        Enum("passed", "failed", "warning", name="result_status"),
        nullable=False
    )
    actual_value = Column(Float, nullable=True)
    expected_value = Column(Float, nullable=True)
    failed_record_count = Column(BigInteger, nullable=True)
    failed_percentage = Column(Float, nullable=True)
    message = Column(Text, nullable=True)

    run = relationship("RuleValidationRun", back_populates="results")
    rule = relationship("QualityRule", back_populates="validation_results")


# ─── Thresholds ──────────────────────────────────────────────────────────────

class QualityThreshold(Base):
    __tablename__ = "quality_thresholds"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    table_id = Column(UUID(as_uuid=False), ForeignKey("table_info.id", ondelete="CASCADE"), nullable=False, index=True)
    column_name = Column(String(255), nullable=True)  # null means table-level
    metric_name = Column(String(100), nullable=False)
    threshold_type = Column(
        Enum("manual", "auto", name="threshold_type"),
        nullable=False,
        default="manual"
    )
    lower_bound = Column(Float, nullable=True)
    upper_bound = Column(Float, nullable=True)
    severity = Column(
        Enum("low", "medium", "high", "critical", name="threshold_severity"),
        nullable=False,
        default="medium"
    )
    is_active = Column(Boolean, default=True, nullable=False)
    created_by = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_by = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    table = relationship("TableInfo")


# ─── Anomaly Detection ────────────────────────────────────────────────────────

class AnomalyDetectionRun(Base):
    __tablename__ = "anomaly_detection_runs"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    table_id = Column(UUID(as_uuid=False), ForeignKey("table_info.id", ondelete="CASCADE"), nullable=False, index=True)
    snapshot_id = Column(String(255), nullable=True)
    batch_date_hour = Column(String(20), nullable=True)
    auc_score = Column(Float, nullable=True)
    drift_status = Column(String(50), nullable=True)  # no_drift / drift_detected / insufficient_data
    threshold_used = Column(Float, nullable=True)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    table = relationship("TableInfo")
    feature_importances = relationship("AnomalyFeatureImportance", back_populates="run", lazy="selectin")


class AnomalyFeatureImportance(Base):
    __tablename__ = "anomaly_feature_importance"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    run_id = Column(UUID(as_uuid=False), ForeignKey("anomaly_detection_runs.id", ondelete="CASCADE"), nullable=False)
    column_name = Column(String(255), nullable=False)
    shap_value = Column(Float, nullable=True)
    importance_rank = Column(Integer, nullable=True)

    run = relationship("AnomalyDetectionRun", back_populates="feature_importances")


# ─── Alerts ──────────────────────────────────────────────────────────────────

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    table_id = Column(UUID(as_uuid=False), ForeignKey("table_info.id", ondelete="CASCADE"), nullable=False, index=True)
    batch_date_hour = Column(String(20), nullable=True)
    snapshot_id = Column(String(255), nullable=True)
    alert_type = Column(String(100), nullable=False)  # rule_fail/metric_threshold/anomaly/freshness/schema_drift/job_failed
    severity = Column(
        Enum("low", "medium", "high", "critical", name="alert_severity"),
        nullable=False,
        default="medium"
    )
    title = Column(String(500), nullable=False)
    message = Column(Text, nullable=True)
    status = Column(
        Enum("open", "acknowledged", "resolved", "ignored", name="alert_status"),
        nullable=False,
        default="open"
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    acknowledged_by = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)

    table = relationship("TableInfo")
    acknowledger = relationship("User", foreign_keys=[acknowledged_by])


# ─── Job Runs ────────────────────────────────────────────────────────────────

class JobRun(Base):
    __tablename__ = "job_runs"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    table_id = Column(UUID(as_uuid=False), ForeignKey("table_info.id", ondelete="SET NULL"), nullable=True, index=True)
    job_name = Column(String(255), nullable=False)  # ingest_data, clean_data, metadata_collection, ...
    dag_id = Column(String(255), nullable=True)
    airflow_run_id = Column(String(500), nullable=True)
    status = Column(
        Enum("pending", "running", "success", "failed", "skipped", name="job_status"),
        nullable=False,
        default="pending"
    )
    batch_date_hour = Column(String(20), nullable=True)
    snapshot_id = Column(String(255), nullable=True)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    triggered_by = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    table = relationship("TableInfo")
    triggerer = relationship("User", foreign_keys=[triggered_by])
