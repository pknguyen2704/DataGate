from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import now
from app.db.base import Base

class Table(Base):
    """
    Model represent the tables that have been discovered and registered 
    from the data lakehouse connection for management and observability.
    """
    __tablename__ = "tables"

    id = Column(Integer, primary_key=True, index=True)
    connection_id = Column(Integer, ForeignKey("connections.id"), nullable=False)
    
    catalog = Column(String, default="iceberg")
    schema_name = Column(String)
    table_name = Column(String)
    
    # Status flags
    is_active = Column(Boolean, default=True) # If false, we stop monitoring/observing this table
    
    # Metadata
    description = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=now())
    updated_at = Column(DateTime, default=now(), onupdate=now())

    # Relationships
    connection = relationship("Connection", back_populates="tables")
