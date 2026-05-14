from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.common_schema import PaginatedResponse, RuleSource, RuleStatus, SeverityLevel
from app.schemas.user_schema import UserLiteOut


class RuleBase(BaseModel):
    table_id: UUID
    column_name: str = Field(..., max_length=255)
    constraint_name: str | None = Field(default=None, max_length=512)
    description: str | None = None
    current_value: str | None = Field(default=None, max_length=255)
    suggesting_rule: str | None = Field(default=None, max_length=255)
    code_for_constraint: str = Field(..., max_length=512)
    rule_description: str | None = None
    frequency: int = 1
    source: RuleSource = RuleSource.MANUAL
    severity_level: SeverityLevel = SeverityLevel.WARNING
    is_active: bool = True


class RuleCreate(BaseModel):
    table_id: UUID
    column_name: str = Field(..., max_length=255)
    constraint_name: str | None = Field(default=None, max_length=512)
    code_for_constraint: str = Field(..., max_length=512)
    severity_level: SeverityLevel = SeverityLevel.WARNING
    description: str | None = None
    frequency: int = 1
    source: RuleSource = RuleSource.MANUAL


class RuleUpdate(BaseModel):
    column_name: str | None = Field(default=None, max_length=255)
    constraint_name: str | None = Field(default=None, max_length=512)
    code_for_constraint: str | None = Field(default=None, max_length=512)
    severity_level: SeverityLevel | None = None
    description: str | None = None
    is_active: bool | None = None
    frequency: int | None = None


class RuleOut(RuleBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: UUID | None = None
    last_modified_by: UUID | None = None
    created_by_user: UserLiteOut | None = None
    last_modified_by_user: UserLiteOut | None = None
    model_config = ConfigDict(from_attributes=True)


class RuleListOut(PaginatedResponse[RuleOut]):
    pass


class RuleVerifyCreate(BaseModel):
    rule_id: UUID
    table_id: UUID
    batch_id: str | None = None
    status: str
    message: str | None = None


class RuleVerifyUpdate(BaseModel):
    is_resolved: bool


class RuleVerifyOut(BaseModel):
    id: UUID
    rule_id: UUID
    table_id: UUID
    batch_id: str | None = None
    status: str
    message: str | None = None
    is_resolved: bool
    created_at: datetime
    rule: RuleOut | None = None
    model_config = ConfigDict(from_attributes=True)