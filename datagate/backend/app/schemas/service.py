from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ServiceBase(BaseModel):
    name: str
    service_type: str
    connection_url: str
    integrated_tables: Optional[list[str]] = []

class ServiceCreate(ServiceBase):
    pass

class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    service_type: Optional[str] = None
    connection_url: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    integrated_tables: Optional[list[str]] = None

class Service(ServiceBase):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ConnectionTest(BaseModel):
    status: str
    message: str
    tables: Optional[list[str]] = None
