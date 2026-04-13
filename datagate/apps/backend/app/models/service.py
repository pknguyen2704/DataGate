from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql.functions import now
from app.db.base_class import Base

class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    service_type = Column(String)  # postgres, mysql, trino, etc.
    connection_url = Column(String)
    status = Column(String, default="healthy")
    integrated_tables = Column(JSON, nullable=True)  # List of table names
    created_at = Column(DateTime, default=now())
    updated_at = Column(DateTime, default=now(), onupdate=now())
