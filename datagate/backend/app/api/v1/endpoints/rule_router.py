from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.db.session import get_db
from app.models import User
from app.rbac.permissions import PermissionCode
from app.schemas import DataRuleCreate, DataRuleStatusUpdate, DataRuleUpdate
from app.services.rule_service import RuleService


rules_router = APIRouter(prefix="/rules", tags=["Rules"])


def get_rule_service(db: Session = Depends(get_db)) -> RuleService:
    return RuleService(db)


@rules_router.get("")
def list_rules(
    service: RuleService = Depends(get_rule_service),
    _user: User = Depends(require_permission(PermissionCode.RULE_VIEW)),
    table_id: Optional[str] = Query(None),
    rule_status: Optional[str] = Query(None),
    top_k: Optional[int] = Query(None, ge=1, le=200),
):
    rules = service.list_rules(table_id=table_id, rule_status=rule_status, top_k=top_k)
    return [service.to_rule_out(rule).model_dump() for rule in rules]


@rules_router.post("", status_code=status.HTTP_201_CREATED)
def create_rule(
    body: DataRuleCreate,
    service: RuleService = Depends(get_rule_service),
    current_user: User = Depends(require_permission(PermissionCode.RULE_CREATE)),
):
    rule = service.create_rule(body, created_by=current_user.id)
    return {"id": rule.id, "constraint_type": rule.constraint_type, "status": rule.status}


@rules_router.patch("/{rule_id}")
def update_rule(
    rule_id: str,
    body: DataRuleUpdate,
    service: RuleService = Depends(get_rule_service),
    current_user: User = Depends(require_permission(PermissionCode.RULE_UPDATE)),
):
    rule = service.update_rule(rule_id, body, modified_by=current_user.id)
    return {"id": rule.id, "status": "updated"}


@rules_router.patch("/{rule_id}/status")
def update_rule_status(
    rule_id: str,
    body: DataRuleStatusUpdate,
    service: RuleService = Depends(get_rule_service),
    current_user: User = Depends(require_permission(PermissionCode.RULE_UPDATE)),
):
    rule = service.update_rule_status(rule_id, body, modified_by=current_user.id)
    return {"id": rule.id, "status": rule.status}


@rules_router.get("/verifications")
def list_rule_verifications(
    table_id: str,
    service: RuleService = Depends(get_rule_service),
    _user: User = Depends(require_permission(PermissionCode.RULE_VIEW)),
    top_k: Optional[int] = Query(None, ge=1, le=200),
):
    results = service.list_rule_verifications(table_id=table_id, top_k=top_k)
    return [service.to_rule_verification_out(result).model_dump() for result in results]


@rules_router.get("/{rule_id}")
def get_rule(
    rule_id: str,
    service: RuleService = Depends(get_rule_service),
    _user: User = Depends(require_permission(PermissionCode.RULE_VIEW)),
):
    rule = service.get_rule_or_404(rule_id)
    return service.to_rule_out(rule).model_dump()


@rules_router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rule(
    rule_id: str,
    service: RuleService = Depends(get_rule_service),
    _user: User = Depends(require_permission(PermissionCode.RULE_DELETE)),
):
    service.delete_rule(rule_id)
    return None
