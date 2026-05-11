from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.db.session import get_db
from app.models import User
from app.rbac.permissions import PermissionCode
from app.schemas.rule_schema import RuleCreate, RuleOut, RuleUpdate, RuleVerifyOut
from app.schemas.table_schema import TableLiteOut
from app.services.rule_service import RuleService


rules_router = APIRouter(prefix="/rules", tags=["Rules"])


def get_rule_service(db: Session = Depends(get_db)) -> RuleService:
    return RuleService(db)


@rules_router.get("/managed-tables", response_model=list[TableLiteOut])
def list_managed_tables(
    service: RuleService = Depends(get_rule_service),
    _user: User = Depends(require_permission(PermissionCode.RULE_VIEW)),
):
    return service.get_managed_tables()


@rules_router.get("", response_model=list[RuleOut])
def list_rules(
    table_id: UUID | None = Query(default=None),
    rule_status: str | None = Query(default=None),
    limit: int | None = Query(default=None, ge=1, le=200),
    service: RuleService = Depends(get_rule_service),
    _user: User = Depends(require_permission(PermissionCode.RULE_VIEW)),
):
    return service.list_rules(str(table_id) if table_id else None, rule_status, limit)


@rules_router.post("", response_model=RuleOut, status_code=status.HTTP_201_CREATED)
def create_rule(
    data: RuleCreate,
    service: RuleService = Depends(get_rule_service),
    current_user: User = Depends(require_permission(PermissionCode.RULE_CREATE)),
):
    return service.create_rule(data, str(current_user.id))


@rules_router.get("/verify-results", response_model=list[RuleVerifyOut])
def list_rule_verify_results(
    table_id: UUID | None = Query(default=None),
    limit: int | None = Query(default=None, ge=1, le=200),
    service: RuleService = Depends(get_rule_service),
    _user: User = Depends(require_permission(PermissionCode.RULE_VIEW)),
):
    return service.list_verify_results(str(table_id) if table_id else None, limit)


@rules_router.patch("/verify-results/{verify_id}/resolve", response_model=RuleVerifyOut)
def resolve_rule_verify_result(
    verify_id: UUID,
    service: RuleService = Depends(get_rule_service),
    _user: User = Depends(require_permission(PermissionCode.RULE_UPDATE)),
):
    return service.set_verify_resolved(str(verify_id), True)


@rules_router.patch("/verify-results/{verify_id}/unresolve", response_model=RuleVerifyOut)
def unresolve_rule_verify_result(
    verify_id: UUID,
    service: RuleService = Depends(get_rule_service),
    _user: User = Depends(require_permission(PermissionCode.RULE_UPDATE)),
):
    return service.set_verify_resolved(str(verify_id), False)


@rules_router.get("/{rule_id}", response_model=RuleOut)
def get_rule(
    rule_id: UUID,
    service: RuleService = Depends(get_rule_service),
    _user: User = Depends(require_permission(PermissionCode.RULE_VIEW)),
):
    return service.get_rule_or_404(str(rule_id))


@rules_router.put("/{rule_id}", response_model=RuleOut)
def update_rule(
    rule_id: UUID,
    data: RuleUpdate,
    service: RuleService = Depends(get_rule_service),
    current_user: User = Depends(require_permission(PermissionCode.RULE_UPDATE)),
):
    return service.update_rule(str(rule_id), data, str(current_user.id))


@rules_router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rule(
    rule_id: UUID,
    service: RuleService = Depends(get_rule_service),
    _user: User = Depends(require_permission(PermissionCode.RULE_DELETE)),
):
    service.delete_rule(str(rule_id))
    return None


@rules_router.patch("/{rule_id}/activate", response_model=RuleOut)
def activate_rule(
    rule_id: UUID,
    service: RuleService = Depends(get_rule_service),
    current_user: User = Depends(require_permission(PermissionCode.RULE_UPDATE)),
):
    return service.set_rule_active(str(rule_id), True, str(current_user.id))


@rules_router.patch("/{rule_id}/inactive", response_model=RuleOut)
def inactive_rule(
    rule_id: UUID,
    service: RuleService = Depends(get_rule_service),
    current_user: User = Depends(require_permission(PermissionCode.RULE_UPDATE)),
):
    return service.set_rule_active(str(rule_id), False, str(current_user.id))
