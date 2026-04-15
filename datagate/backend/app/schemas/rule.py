from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ActiveRuleBase(BaseModel):
    table_name: str
    column_name: str
    rule_type: str
    rule_expression: str
    category: str = "validity"
    priority: str = "medium"
    source: str = "manual"
    description: Optional[str] = None
    confidence_score: Optional[float] = None
    frequency: int = 1
    last_seen: Optional[datetime] = None
    is_active: bool = True
    is_applied: bool = False
    last_result_status: Optional[str] = None
    last_failure_message: Optional[str] = None
    last_validated_at: Optional[datetime] = None

class ActiveRuleCreate(ActiveRuleBase):
    pass

class ActiveRuleUpdate(BaseModel):
    is_active: Optional[bool] = None
    is_applied: Optional[bool] = None
    rule_expression: Optional[str] = None
    frequency: Optional[int] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    description: Optional[str] = None
    confidence_score: Optional[float] = None
    last_result_status: Optional[str] = None
    last_failure_message: Optional[str] = None
    last_validated_at: Optional[datetime] = None

class ActiveRule(ActiveRuleBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class RuleSuggestionCreate(BaseModel):
    table_name: str
    column_name: str
    rule_type: str
    rule_expression: str
    category: str = "validity"
    priority: str = "medium"
    description: Optional[str] = None
    confidence_score: Optional[float] = None
    source: str = "pydeequ"


class RuleSuggestionBatch(BaseModel):
    table_name: str
    suggestions: list[RuleSuggestionCreate]
