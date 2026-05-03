from sqlalchemy.orm import Session, selectinload

from app.core.exceptions import BadRequestError, NotFoundError
from app.models import Rule, RuleVerificationResult, Table
from app.schemas.rule import (
    DataRuleCreate,
    DataRuleOut,
    DataRuleStatusUpdate,
    DataRuleUpdate,
    RuleVerificationResultOut,
)


class RuleService:
    def __init__(self, db: Session):
        self.db = db

    def list_rules(
        self,
        table_id: str | None = None,
        rule_status: str | None = None,
        top_k: int | None = None,
    ) -> list[Rule]:
        query = self.db.query(Rule)

        if table_id:
            query = query.filter(Rule.table_id == table_id)
        if rule_status:
            query = query.filter(Rule.status == rule_status)

        query = query.order_by(Rule.frequency.desc(), Rule.updated_at.desc(), Rule.created_at.desc())

        if top_k:
            query = query.limit(top_k)

        return query.all()

    def create_rule(
        self,
        body: DataRuleCreate,
        created_by: str,
    ) -> Rule:
        table = self.db.query(Table).filter(Table.id == body.table_id).first()
        if table is None:
            raise NotFoundError("Table not found")

        existing_manual_rule = (
            self.db.query(Rule)
            .filter(
                Rule.table_id == body.table_id,
                Rule.column_name == body.column_name,
                Rule.constraint_type == body.constraint_type,
                Rule.source == "manual",
            )
            .first()
        )
        if existing_manual_rule:
            raise BadRequestError("A manual rule with the same column and constraint type already exists")

        rule = Rule(
            table_id=body.table_id,
            column_name=body.column_name,
            constraint_type=body.constraint_type,
            description=body.description,
            source="manual",
            status="active",
            frequency=1,
            created_by=created_by,
            last_modified_by=created_by,
        )
        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)
        return rule

    def get_rule_by_id(self, rule_id: str) -> Rule | None:
        return (
            self.db.query(Rule)
            .options(selectinload(Rule.verification_results))
            .filter(Rule.id == rule_id)
            .first()
        )

    def get_rule_or_404(self, rule_id: str) -> Rule:
        rule = self.get_rule_by_id(rule_id)
        if rule is None:
            raise NotFoundError("Rule not found")
        return rule

    def update_rule(
        self,
        rule_id: str,
        body: DataRuleUpdate,
        modified_by: str,
    ) -> Rule:
        rule = self.get_rule_or_404(rule_id)

        for field, value in body.model_dump(exclude_unset=True).items():
            setattr(rule, field, value)

        if rule.status == "pending":
            rule.status = "active"

        rule.last_modified_by = modified_by
        self.db.commit()
        self.db.refresh(rule)
        return rule

    def update_rule_status(
        self,
        rule_id: str,
        body: DataRuleStatusUpdate,
        modified_by: str,
    ) -> Rule:
        rule = self.get_rule_or_404(rule_id)
        rule.status = body.status
        rule.last_modified_by = modified_by
        self.db.commit()
        self.db.refresh(rule)
        return rule

    def delete_rule(self, rule_id: str) -> None:
        rule = self.get_rule_or_404(rule_id)
        self.db.delete(rule)
        self.db.commit()

    def list_rule_verifications(
        self,
        table_id: str,
        top_k: int | None = None,
    ) -> list[RuleVerificationResult]:
        query = (
            self.db.query(RuleVerificationResult)
            .options(selectinload(RuleVerificationResult.rule))
            .filter(RuleVerificationResult.table_id == table_id)
            .order_by(
                RuleVerificationResult.batch_date_hour.desc(),
                RuleVerificationResult.verified_at.desc(),
            )
        )

        if top_k:
            query = query.limit(top_k)

        return query.all()

    def to_rule_out(self, rule: Rule) -> DataRuleOut:
        return DataRuleOut(
            id=rule.id,
            table_id=rule.table_id,
            column_name=rule.column_name,
            constraint_type=rule.constraint_type,
            created_by=rule.source,
            status=rule.status,
            description=rule.description,
            frequency=rule.frequency,
            first_seen_at_date_hour=rule.first_seen_at_date_hour,
            last_seen_at_date_hour=rule.last_seen_at_date_hour,
            constraint_name=rule.constraint_name,
            current_value=rule.current_value,
            suggesting_rule=rule.suggesting_rule,
            code_for_constraint=rule.code_for_constraint,
            suggested_at_date_hour=rule.suggested_at_date_hour,
            created_by_user_id=rule.created_by,
            last_modified_by_user_id=rule.last_modified_by,
            created_at=rule.created_at,
            updated_at=rule.updated_at,
        )

    def to_rule_verification_out(self, result: RuleVerificationResult) -> RuleVerificationResultOut:
        return RuleVerificationResultOut(
            id=result.id,
            rule_id=result.rule_id,
            table_id=result.table_id,
            column_name=result.rule.column_name if result.rule else None,
            constraint_type=result.rule.constraint_type if result.rule else None,
            batch_date_hour=result.batch_date_hour,
            verification_status=result.verification_status,
            actual_value=result.actual_value,
            expected_value=result.expected_value,
            failure_count=result.failure_count,
            total_count=result.total_count,
            message=result.message,
            verified_at=result.verified_at,
        )
