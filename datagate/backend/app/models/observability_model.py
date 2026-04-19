from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, BigInteger, Date, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import now
from app.db.base import Base

# Bảng cấu hình quản lý việc quét (scan) dữ liệu Observability cho từng bảng
class DGObservabilityConfig(Base):
    __tablename__ = "dg_observability_config"

    id = Column(Integer, primary_key=True, index=True)
    catalog = Column(Text, default="iceberg")
    schema_name = Column(Text, default="public")
    table_name = Column(Text) # Tên bảng cần theo dõi
    is_active = Column(Boolean, default=True) # Cờ bật/tắt (kết nối với UI để quyết định Airflow có chạy hay không)
    last_run_at = Column(DateTime, nullable=True) # Lưu lại thời điểm quét metadata lần cuối
    created_at = Column(DateTime, default=now())

# Bảng lưu lịch sử các lần chạy (scan run) do Airflow trigger
class DGObservabilityRunHistory(Base):
    __tablename__ = "dg_observability_run_history"

    id = Column(BigInteger, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("dg_observability_config.id"), nullable=True)
    dag_id = Column(Text)
    dag_run_id = Column(Text)
    trigger_type = Column(Text, default="scheduled") # Loại trigger (scheduled, manual)
    status = Column(Text, default="queued") # Trạng thái chạy (queued, running, success, failed)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=now())

# Bảng lưu các thông số Freshness (độ trễ) và Size (kích thước tổng) của bảng tại một thời điểm quét
class DGObservabilitySnapshot(Base):
    __tablename__ = "dg_observability_snapshots"

    id = Column(BigInteger, primary_key=True, index=True)
    table_name = Column(Text) # Tên bảng được quét
    snapshot_time = Column(DateTime) # Thời điểm thực hiện quét
    last_updated_time = Column(DateTime) # Freshness: Thời điểm dòng dữ liệu cuối cùng được đưa vào hệ thống
    total_records = Column(BigInteger) # Volume cơ bản: Tổng số dòng hiện có
    total_size = Column(BigInteger) # Tổng kích thước dữ liệu (bytes)
    created_at = Column(DateTime, default=now())

# Bảng lưu lịch sử gia tăng Volume (khối lượng dữ liệu nạp vào theo từng ngày) để Prophet dự đoán
class DGObservabilityVolumeTS(Base):
    __tablename__ = "dg_observability_volume_ts"

    id = Column(BigInteger, primary_key=True, index=True)
    table_name = Column(Text) # Tên bảng
    dt = Column(Date) # Ngày nạp dữ liệu (Date truncate)
    records_added = Column(BigInteger) # Số lượng records được nạp mới trong ngày đó
    created_at = Column(DateTime, default=now())

# Bảng lưu lại cấu trúc schema (danh sách cột, kiểu dữ liệu) của bảng tại mỗi lần quét để so sánh drift
class DGObservabilitySchema(Base):
    __tablename__ = "dg_observability_schema"

    id = Column(BigInteger, primary_key=True, index=True)
    table_name = Column(Text) # Tên bảng
    column_name = Column(Text) # Tên cột
    data_type = Column(Text) # Kiểu dữ liệu của cột
    snapshot_time = Column(DateTime) # Khớp với snapshot_time của bảng DGObservabilitySnapshot
    created_at = Column(DateTime, default=now())

# Bảng lưu danh sách các cảnh báo / bất thường (Incidents) được Prophet và hệ thống phát hiện
class DGObservabilityIncident(Base):
    __tablename__ = "dg_observability_incidents"

    id = Column(BigInteger, primary_key=True, index=True)
    table_name = Column(Text) # Tên bảng bị lỗi
    incident_type = Column(String) # Loại lỗi: drift (schema thay đổi), freshness (trễ), volume (tăng/giảm bất thường)
    severity = Column(String) # Mức độ nghiêm trọng: low, medium, high
    message = Column(Text) # Lời giải thích chi tiết về lỗi
    status = Column(String, default="open") # Trạng thái xử lý: open, resolved
    detected_at = Column(DateTime, default=now()) # Thời điểm phát hiện
    created_at = Column(DateTime, default=now())

# Bảng lưu các chỉ số thống kê chi tiết (Metrics) cấp độ cột (Column-level)
class DGObservabilityMetric(Base):
    __tablename__ = "dg_observability_metrics"

    id = Column(BigInteger, primary_key=True, index=True)
    table_name = Column(Text) # Tên bảng (schema.table)
    column_name = Column(Text) # Tên cột (dùng '*' nếu là chỉ số cấp bảng như row_count)
    metric_name = Column(Text) # Tên chỉ số: null_percentage, uniqueness, mean, min, max, stddev
    metric_value = Column(Float) # Giá trị đo được
    snapshot_time = Column(DateTime) # Thời điểm thực hiện đo (Analysis time)
    created_at = Column(DateTime, default=now())

# Bảng lưu cấu hình ngưỡng cố định (Fixed Thresholds) cho từng chỉ số
class DGObservabilityMetricThreshold(Base):
    __tablename__ = "dg_observability_metric_thresholds"

    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(Text)
    column_name = Column(Text)
    metric_name = Column(Text)
    min_value = Column(Float, nullable=True) # Ngưỡng tối thiểu (SLA)
    max_value = Column(Float, nullable=True) # Ngưỡng tối đa
    created_at = Column(DateTime, default=now())
