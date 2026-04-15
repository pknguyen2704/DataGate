from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float
from sqlalchemy.sql.functions import now
from app.db.base_class import Base

class ActiveRule(Base):
    __tablename__ = "active_rules"

    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String)
    column_name = Column(String)
    rule_type = Column(String)
    rule_expression = Column(Text, unique=True)
    category = Column(String, default="validity")
    priority = Column(String, default="medium")
    source = Column(String, default="manual")
    description = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True)
    frequency = Column(Integer, default=1)
    last_seen = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    is_applied = Column(Boolean, default=False)
    last_result_status = Column(String, nullable=True)
    last_failure_message = Column(Text, nullable=True)
    last_validated_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=now())
