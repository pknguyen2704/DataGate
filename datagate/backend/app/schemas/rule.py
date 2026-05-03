# Data quality rule schemas — system-suggested and user-defined rules.
#
# Constraint types (UI dropdown):
#   not_null     — column must not be NULL           (Deequ: CompletenessConstraint)
#   non_negative — column value >= 0                 (Deequ: ComplianceConstraint)
#   unique       — all values must be unique         (Deequ: UniquenessConstraint)
#   value_range  — value must be in an allowed set   (Deequ: ComplianceConstraint IN)
#   range_check  — value between min/max             (manual only)
#   regex        — value matches a regex pattern     (manual only)
#
# Source: "system" (Spark/Deequ job) | "manual" (user via UI)
# Status: "pending" → "active" | "inactive"
from __future__ import annotations
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel


RuleSource     = Literal["system", "manual"]
RuleStatus     = Literal["pending", "active", "inactive"]
RuleVerificationStatus = Literal["passed", "failed", "error"]
ConstraintType = Literal[
    "not_null", "non_negative", "unique", "value_range", "range_check", "regex"
]


class DataRuleOut(BaseModel):
    """Full rule representation returned to the client."""
    id: str
    table_id: str
    column_name: str
    constraint_type: ConstraintType
    created_by: RuleSource
    status: RuleStatus
    description: Optional[str] = None
    frequency: int = 1
    first_seen_at_date_hour: Optional[str] = None
    last_seen_at_date_hour: Optional[str] = None
    # System-rule provenance (populated by Spark/Deequ ingest job)
    constraint_name: Optional[str] = None
    current_value: Optional[str] = None
    suggesting_rule: Optional[str] = None
    code_for_constraint: Optional[str] = None
    suggested_at_date_hour: Optional[str] = None
    # Authorship
    created_by_user_id: Optional[str] = None
    last_modified_by_user_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DataRuleCreate(BaseModel):
    """Create a manual rule via the UI dropdown."""
    table_id: str
    column_name: str
    constraint_type: ConstraintType
    description: Optional[str] = None


class DataRuleUpdate(BaseModel):
    """User edits to an existing rule (system or manual)."""
    description: Optional[str] = None


class DataRuleStatusUpdate(BaseModel):
    """Accept / reject / disable a rule."""
    status: RuleStatus


class DataRuleSummary(BaseModel):
    """Lightweight row for list views."""
    id: str
    table_id: str
    column_name: str
    constraint_type: ConstraintType
    created_by: RuleSource
    status: RuleStatus
    description: Optional[str] = None
    frequency: int = 1
    first_seen_at_date_hour: Optional[str] = None
    last_seen_at_date_hour: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RuleVerificationResultOut(BaseModel):
    id: str
    rule_id: str
    table_id: str
    column_name: Optional[str] = None
    constraint_type: Optional[ConstraintType] = None
    batch_date_hour: str
    verification_status: RuleVerificationStatus
    actual_value: Optional[str] = None
    expected_value: Optional[str] = None
    failure_count: Optional[int] = None
    total_count: Optional[int] = None
    message: Optional[str] = None
    verified_at: datetime

    model_config = {"from_attributes": True}
