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


from app.schemas.rule_schema import RuleCreate, RuleOut, RuleUpdate, RuleVerifyOut, RuleListOut


@rules_router.get("", response_model=RuleListOut)
def list_rules(
    table_id: UUID | None = Query(default=None),
    column_name: str | None = Query(default=None),
    source: str | None = Query(default=None),
    rule_status: str | None = Query(default=None),
    severity_level: str | None = Query(default=None),
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    service: RuleService = Depends(get_rule_service),
    _user: User = Depends(require_permission(PermissionCode.RULE_VIEW)),
):
    return service.list_rules(
        table_id=str(table_id) if table_id else None, 
        column_name=column_name, 
        source=source, 
        rule_status=rule_status, 
        severity_level=severity_level, 
        search=search,
        page=page,
        page_size=page_size
    )


@rules_router.post("", response_model=RuleOut, status_code=status.HTTP_201_CREATED)
def create_rule(
    data: RuleCreate,
    service: RuleService = Depends(get_rule_service),
    current_user: User = Depends(require_permission(PermissionCode.RULE_CREATE)),
):
    return service.create_rule(data, str(current_user.id))


@rules_router.get("/{rule_id}", response_model=RuleOut)
def get_rule(
    rule_id: UUID,
    service: RuleService = Depends(get_rule_service),
    _user: User = Depends(require_permission(PermissionCode.RULE_VIEW)),
):
    return service.get_rule_or_404(str(rule_id))


@rules_router.patch("/{rule_id}", response_model=RuleOut)
def update_rule(
    rule_id: UUID,
    data: RuleUpdate,
    service: RuleService = Depends(get_rule_service),
    current_user: User = Depends(require_permission(PermissionCode.RULE_UPDATE)),
):
    return service.update_rule(str(rule_id), data, str(current_user.id))


@rules_router.post("/{rule_id}/approve", response_model=RuleOut)
def approve_rule(
    rule_id: UUID,
    service: RuleService = Depends(get_rule_service),
    current_user: User = Depends(require_permission(PermissionCode.RULE_ENABLE_DISABLE)),
):
    return service.set_rule_status(str(rule_id), "active", str(current_user.id))


@rules_router.post("/{rule_id}/deactivate", response_model=RuleOut)
def deactivate_rule(
    rule_id: UUID,
    service: RuleService = Depends(get_rule_service),
    current_user: User = Depends(require_permission(PermissionCode.RULE_ENABLE_DISABLE)),
):
    return service.set_rule_status(str(rule_id), "inactive", str(current_user.id))


@rules_router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rule(
    rule_id: UUID,
    service: RuleService = Depends(get_rule_service),
    _user: User = Depends(require_permission(PermissionCode.RULE_DELETE)),
):
    service.delete_rule(str(rule_id))
    return None


@rules_router.get("/verify-results/all", response_model=list[RuleVerifyOut])
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
