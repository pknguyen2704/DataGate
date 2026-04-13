from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ActiveRuleBase(BaseModel):
    table_name: str
    column_name: str
    rule_type: str
    rule_expression: str
    frequency: int = 1
    last_seen: Optional[datetime] = None
    is_active: bool = True

class ActiveRuleCreate(ActiveRuleBase):
    pass

class ActiveRuleUpdate(BaseModel):
    is_active: Optional[bool] = None
    rule_expression: Optional[str] = None
    frequency: Optional[int] = None

class ActiveRule(ActiveRuleBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
