from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

class ConnectionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, example="Trino_Production")
    description: Optional[str] = Field(None, max_length=500)
    connection_url: str = Field(..., min_length=1, example="trino://user@localhost:8080")
    integrated_tables: Optional[List[str]] = Field(default_factory=list)

class ConnectionCreate(ConnectionBase):
    pass

class ConnectionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    connection_url: Optional[str] = None
    integrated_tables: Optional[List[str]] = None

class ConnectionOut(ConnectionBase):
    id: int
    owner: Optional[dict] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ConnectionTestResult(BaseModel):
    status: str
    message: str
    schemas: List[str] = Field(default_factory=list)
    tables: List[str] = Field(default_factory=list)

class ConnectionExplore(BaseModel):
    connection: ConnectionOut
    schemas: List[str]
    tables: List[str]
