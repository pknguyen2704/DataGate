from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.db.session import get_db
from app.models import User
from app.rbac.permissions import PermissionCode
from app.schemas.dashboard_schema import QualityResultOut
from app.services.dashboard_service import DashboardService

quality_router = APIRouter(prefix="/quality", tags=["Quality"])

def get_dashboard_service(db: Session = Depends(get_db)) -> DashboardService:
    return DashboardService(db)


@quality_router.get("/results", response_model=list[QualityResultOut])
def quality_results(
    result_type: str | None = Query(default=None),
    unresolved_only: bool = Query(default=False),
    table_id: str | None = Query(default=None),
    service: DashboardService = Depends(get_dashboard_service),
    _user: User = Depends(require_permission(PermissionCode.QUALITY_VIEW)),
):
    return service.quality_results(result_type, unresolved_only, table_id)


@quality_router.get("/metadata-results", response_model=list[QualityResultOut])
def metadata_results(service: DashboardService = Depends(get_dashboard_service), _user: User = Depends(require_permission(PermissionCode.QUALITY_VIEW))):
    return service.quality_results(result_type="metadata")


@quality_router.get("/profiling-results", response_model=list[QualityResultOut])
def profiling_results(service: DashboardService = Depends(get_dashboard_service), _user: User = Depends(require_permission(PermissionCode.QUALITY_VIEW))):
    return service.quality_results(result_type="profiling")


@quality_router.get("/rule-results", response_model=list[QualityResultOut])
def rule_results(service: DashboardService = Depends(get_dashboard_service), _user: User = Depends(require_permission(PermissionCode.QUALITY_VIEW))):
    return service.quality_results(result_type="rule")


@quality_router.get("/anomaly-results", response_model=list[QualityResultOut])
def anomaly_results(service: DashboardService = Depends(get_dashboard_service), _user: User = Depends(require_permission(PermissionCode.QUALITY_VIEW))):
    return service.quality_results(result_type="anomaly")


@quality_router.get("/unresolved-failures", response_model=list[QualityResultOut])
def unresolved_failures(service: DashboardService = Depends(get_dashboard_service), _user: User = Depends(require_permission(PermissionCode.QUALITY_VIEW))):
    return service.quality_results(unresolved_only=True)
