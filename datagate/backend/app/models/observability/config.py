from sqlalchemy import Column, Integer, Text, Boolean, DateTime
from sqlalchemy.sql.functions import now
from app.db.base import Base

class ObservabilityConfig(Base):
    __tablename__ = "observability_config"

    id = Column(Integer, primary_key=True, index=True)
    catalog = Column(Text, default="iceberg")
    schema_name = Column(Text, default="public")
    table_name = Column(Text) # Tên bảng cần theo dõi
    is_active = Column(Boolean, default=True) # Cờ bật/tắt
    last_run_at = Column(DateTime, nullable=True) # Lưu lại thời điểm quét metadata lần cuối
    created_at = Column(DateTime, default=now())
