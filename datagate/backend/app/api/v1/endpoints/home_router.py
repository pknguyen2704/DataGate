from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.db.session import get_db
from app.models import User
from app.rbac.permissions import PermissionCode
from app.schemas.dashboard_schema import FailureSummaryOut, PlatformOverviewOut, TimelineStatsOut, SchemaHealthOut, TableHealthOut
from app.services.dashboard_service import DashboardService


home_router = APIRouter(prefix="/health", tags=["Health"])


def get_dashboard_service(db: Session = Depends(get_db)) -> DashboardService:
    return DashboardService(db)


@home_router.get("/overview", response_model=PlatformOverviewOut)
def platform_overview(
    schema_name: str | None = Query(default=None),
    service: DashboardService = Depends(get_dashboard_service),
    _user: User = Depends(require_permission(PermissionCode.QUALITY_VIEW)),
):
    return service.get_platform_overview(schema_name)


@home_router.get("/timeline", response_model=list[TimelineStatsOut])
def timeline_stats(
    schema_name: str | None = Query(default=None),
    service: DashboardService = Depends(get_dashboard_service),
    _user: User = Depends(require_permission(PermissionCode.QUALITY_VIEW)),
):
    return service.get_timeline_stats(schema_name)


@home_router.get("/schemas", response_model=list[SchemaHealthOut])
def schema_healths(
    processing_date_hour: datetime | None = Query(default=None),
    service: DashboardService = Depends(get_dashboard_service),
    _user: User = Depends(require_permission(PermissionCode.QUALITY_VIEW)),
):
    return service.schema_healths(processing_date_hour)


@home_router.get("/schemas/{schema_name}", response_model=SchemaHealthOut)
def schema_health(
    schema_name: str,
    processing_date_hour: datetime | None = Query(default=None),
    service: DashboardService = Depends(get_dashboard_service),
    _user: User = Depends(require_permission(PermissionCode.QUALITY_VIEW)),
):
    for item in service.schema_healths(processing_date_hour):
        if item["schema_name"] == schema_name:
            return item
    return {"schema_name": schema_name, "table_count": 0, "critical_fail_count": 0, "warning_fail_count": 0, "total_check_count": 0}


@home_router.get("/tables", response_model=list[TableHealthOut])
def table_healths(
    processing_date_hour: datetime | None = Query(default=None),
    service: DashboardService = Depends(get_dashboard_service),
    _user: User = Depends(require_permission(PermissionCode.QUALITY_VIEW)),
):
    return service.table_healths(processing_date_hour)


@home_router.get("/tables/{table_id}", response_model=TableHealthOut)
def table_health(
    table_id: UUID,
    processing_date_hour: datetime | None = Query(default=None),
    service: DashboardService = Depends(get_dashboard_service),
    _user: User = Depends(require_permission(PermissionCode.QUALITY_VIEW)),
):
    return service.table_health(str(table_id), processing_date_hour)
