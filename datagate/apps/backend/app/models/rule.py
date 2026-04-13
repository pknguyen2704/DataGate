from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql.functions import now
from app.db.base_class import Base

class ActiveRule(Base):
    __tablename__ = "active_rules"

    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String)
    column_name = Column(String)
    rule_type = Column(String)
    rule_expression = Column(Text, unique=True)
    frequency = Column(Integer, default=1)
    last_seen = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=now())
