from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import now
from app.db.base import Base

class Connection(Base):
    """
    Model đại diện cho kết nối duy nhất của hệ thống tới Data Lakehouse (Trino).
    """
    __tablename__ = "connections"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, default="Default Trino Connection")
    description = Column(String, nullable=True)
    connection_url = Column(String)                 # Chuỗi kết nối Trino

    # RELATIONSHIPS
    tables = relationship("Table", back_populates="connection", cascade="all, delete-orphan")
    
    # TIMESTAMPS
    created_at = Column(DateTime, default=now())
    updated_at = Column(DateTime, default=now(), onupdate=now())
