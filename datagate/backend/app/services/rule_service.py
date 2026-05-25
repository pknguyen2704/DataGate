from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.models import QualityCheckResult, Rule, Table
from app.schemas.rule_schema import RuleCreate, RuleUpdate


class RuleService:
    def __init__(self, db: Session):
        self.db = db

    def list_rules(
        self,
        table_id: str | None = None,
        column_name: str | None = None,
        source: str | None = None,
        rule_status: str | None = None,
        severity_level: str | None = None,
        search: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> dict:
        query = self.db.query(Rule)
        if table_id:
            query = query.filter(Rule.table_id == table_id)
        if column_name:
            query = query.filter(Rule.column_name == column_name)
        if source:
            query = query.filter(Rule.source == source)

        if search:
            from sqlalchemy import or_

            search_filter = f"%{search}%"
            query = query.filter(
                or_(
                    Rule.column_name.ilike(search_filter),
                    Rule.constraint_name.ilike(search_filter),
                    Rule.description.ilike(search_filter),
                    Rule.code_for_constraint.ilike(search_filter),
                )
            )

        if rule_status:
            if rule_status == "active":
                query = query.filter(Rule.is_active.is_(True))
            elif rule_status == "inactive":
                query = query.filter(Rule.is_active.is_(False))

        if severity_level:
            query = query.filter(Rule.severity_level == severity_level)

        total = query.count()
        from sqlalchemy import case

        items = (
            query.options(
                joinedload(Rule.created_by_user), joinedload(Rule.last_modified_by_user)
            )
            .order_by(
                Rule.is_active.desc(),
                case({"critical": 0, "warning": 1}, value=Rule.severity_level).asc(),
                Rule.frequency.desc(),
            )
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return {"items": items, "total": total, "page": page, "page_size": page_size}

    def get_rule_or_404(self, rule_id: str) -> Rule:
        rule = (
            self.db.query(Rule)
            .options(
                joinedload(Rule.created_by_user), joinedload(Rule.last_modified_by_user)
            )
            .filter(Rule.id == rule_id)
            .first()
        )
        if not rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found"
            )
        return rule

    def create_rule(self, data: RuleCreate, user_id: str) -> Rule:
        # Check if table exists
        table = self.db.query(Table).filter(Table.id == str(data.table_id)).first()
        if not table:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Table not found"
            )

        rule_dict = data.model_dump()
        # If manual, active by default. If system, inactive by default.
        if rule_dict.get("source") == "system":
            rule_dict["is_active"] = False
        else:
            rule_dict["is_active"] = True

        rule = Rule(**rule_dict, created_by=user_id, last_modified_by=user_id)

        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)
        return rule

    def update_rule(self, rule_id: str, data: RuleUpdate, user_id: str) -> Rule:
        rule = self.get_rule_or_404(rule_id)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(rule, field, value)

        rule.last_modified_by = user_id
        self.db.commit()
        self.db.refresh(rule)
        return rule

    def set_rule_status(self, rule_id: str, status_value: str, user_id: str) -> Rule:
        rule = self.get_rule_or_404(rule_id)
        if status_value == "active":
            rule.is_active = True
        elif status_value == "inactive":
            rule.is_active = False

        rule.last_modified_by = user_id
        self.db.commit()
        self.db.refresh(rule)
        return rule

    def delete_rule(self, rule_id: str) -> None:
        rule = self.get_rule_or_404(rule_id)
        self.db.delete(rule)
        self.db.commit()

    def list_verify_results(
        self, table_id: str | None = None, limit: int | None = None
    ) -> list[QualityCheckResult]:
        query = self.db.query(QualityCheckResult).filter(
            QualityCheckResult.check_type == "rule"
        )
        if table_id:
            query = query.filter(QualityCheckResult.table_id == table_id)
        query = query.order_by(
            QualityCheckResult.processing_date_hour.desc(),
            QualityCheckResult.updated_at.desc(),
        )
        if limit:
            query = query.limit(limit)
        return query.all()

    def set_verify_resolved(self, verify_id: str, is_resolved: bool) -> QualityCheckResult:
        result = (
            self.db.query(QualityCheckResult)
            .filter(
                QualityCheckResult.id == verify_id,
                QualityCheckResult.check_type == "rule",
            )
            .first()
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rule verify result not found",
            )
        result.is_resolved = is_resolved
        self.db.commit()
        self.db.refresh(result)
        return result

    def get_managed_tables(self) -> list[Table]:
        return (
            self.db.query(Table)
            .join(Rule, Rule.table_id == Table.id)
            .distinct()
            .order_by(Table.schema_name, Table.table_name)
            .all()
        )
