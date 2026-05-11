from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Rule, RuleVerify, Table
from app.schemas.rule_schema import RuleCreate, RuleUpdate


class RuleService:
    def __init__(self, db: Session):
        self.db = db

    def list_rules(self, table_id: str | None = None, rule_status: str | None = None, limit: int | None = None) -> list[Rule]:
        query = self.db.query(Rule)
        if table_id:
            query = query.filter(Rule.table_id == table_id)
        if rule_status:
            query = query.filter(Rule.status == rule_status)
        query = query.order_by(Rule.frequency.desc(), Rule.updated_at.desc(), Rule.created_at.desc())
        if limit:
            query = query.limit(limit)
        return query.all()

    def get_rule_or_404(self, rule_id: str) -> Rule:
        rule = self.db.query(Rule).filter(Rule.id == rule_id).first()
        if not rule:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")
        return rule

    def create_rule(self, data: RuleCreate, user_id: str) -> Rule:
        table = self.db.query(Table).filter(Table.id == str(data.table_id)).first()
        if not table:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")
        rule = Rule(**data.model_dump(), created_by=user_id, last_modified_by=user_id)
        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)
        return rule

    def update_rule(self, rule_id: str, data: RuleUpdate, user_id: str) -> Rule:
        rule = self.get_rule_or_404(rule_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(rule, field, value)
        rule.last_modified_by = user_id
        self.db.commit()
        self.db.refresh(rule)
        return rule

    def set_rule_active(self, rule_id: str, is_active: bool, user_id: str) -> Rule:
        rule = self.get_rule_or_404(rule_id)
        rule.status = "active" if is_active else "inactive"
        rule.last_modified_by = user_id
        self.db.commit()
        self.db.refresh(rule)
        return rule

    def delete_rule(self, rule_id: str) -> None:
        rule = self.get_rule_or_404(rule_id)
        self.db.delete(rule)
        self.db.commit()

    def list_verify_results(self, table_id: str | None = None, limit: int | None = None) -> list[RuleVerify]:
        query = self.db.query(RuleVerify).join(RuleVerify.rule)
        if table_id:
            query = query.filter(Rule.table_id == table_id)
        query = query.order_by(RuleVerify.processing_date_hour.desc(), RuleVerify.updated_at.desc())
        if limit:
            query = query.limit(limit)
        return query.all()

    def set_verify_resolved(self, verify_id: str, is_resolved: bool) -> RuleVerify:
        result = self.db.query(RuleVerify).filter(RuleVerify.id == verify_id).first()
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule verify result not found")
        result.is_resolved = is_resolved
        self.db.commit()
        self.db.refresh(result)
        return result

    def get_managed_tables(self) -> list[Table]:
        return (
            self.db.query(Table)
            .join(Rule, Rule.table_id == Table.id)
            .filter(Table.is_active.is_(True))
            .distinct()
            .order_by(Table.schema_name, Table.table_name)
            .all()
        )
