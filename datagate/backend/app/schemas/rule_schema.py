from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID

from app.schemas.common_schema import RuleSource, RuleStatus, SeverityLevel


class RuleBase(BaseModel):
    table_id: UUID

    source: RuleSource = RuleSource.MANUAL
    status: RuleStatus = RuleStatus.PENDING
    severity_level: SeverityLevel = SeverityLevel.WARNING

    column_name: str = Field(..., max_length=255)
    constraint_name: str | None = Field(default=None, max_length=512)
    description: str | None = None

    frequency: int = Field(default=1, ge=1)
    current_value: str | None = Field(default=None, max_length=255)
    suggesting_rule: str | None = Field(default=None, max_length=255)
    code_for_constraint: str = Field(..., max_length=512)
    rule_description: str | None = None

    created_by: UUID | None = None
    last_modified_by: UUID | None = None


class RuleCreate(RuleBase):
    pass


class RuleUpdate(BaseModel):
    source: RuleSource | None = None
    status: RuleStatus | None = None
    severity_level: SeverityLevel | None = None

    column_name: str | None = Field(default=None, max_length=255)
    constraint_name: str | None = Field(default=None, max_length=512)
    description: str | None = None

    frequency: int | None = Field(default=None, ge=1)
    current_value: str | None = Field(default=None, max_length=255)
    suggesting_rule: str | None = Field(default=None, max_length=255)
    code_for_constraint: str | None = Field(default=None, max_length=512)
    rule_description: str | None = None

    last_modified_by: UUID | None = None


class RuleOut(RuleBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RuleVerifyBase(BaseModel):
    rule_id: UUID
    constraint_status: str = Field(..., max_length=50)
    constraint_message: str | None = None
    processing_date_hour: datetime


class RuleVerifyCreate(RuleVerifyBase):
    pass


class RuleVerifyUpdate(BaseModel):
    constraint_status: str | None = Field(default=None, max_length=50)
    constraint_message: str | None = None


class RuleVerifyOut(RuleVerifyBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)