from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.db.session import get_db
from app.models import User
from app.rbac.permissions import PermissionCode
from app.schemas.dashboard_schema import (
    GrafanaEmbedUrlOut, GrafanaVariablesOut, 
    ManagedSchemaNodeOut, TimeRangeOut
)
from app.services.dashboard_service import DashboardService

observability_router = APIRouter(prefix="/observability", tags=["Observability"])


def get_dashboard_service(db: Session = Depends(get_db)) -> DashboardService:
    return DashboardService(db)


@observability_router.get("/tables/{table_id}/default-time-range", response_model=TimeRangeOut)
def default_time_range(
    table_id: UUID,
    service: DashboardService = Depends(get_dashboard_service),
    _user: User = Depends(require_permission(PermissionCode.DASHBOARD_VIEW)),
):
    return service.get_default_time_range(str(table_id))


@observability_router.get("/tables/{table_id}/dashboard", response_model=GrafanaEmbedUrlOut)
def grafana_dashboard(
    table_id: UUID,
    from_time: datetime | None = Query(default=None),
    to_time: datetime | None = Query(default=None),
    service: DashboardService = Depends(get_dashboard_service),
    _user: User = Depends(require_permission(PermissionCode.DASHBOARD_VIEW)),
):
    url = service.get_grafana_dashboard_url(
        table_id=str(table_id),
        from_time=from_time,
        to_time=to_time
    )
    return {"url": url}


@observability_router.get("/managed-tree", response_model=list[ManagedSchemaNodeOut])
def managed_tree(
    service: DashboardService = Depends(get_dashboard_service),
    _user: User = Depends(require_permission(PermissionCode.DASHBOARD_VIEW)),
):
    return service.managed_tree()


@observability_router.get("/grafana/variables", response_model=GrafanaVariablesOut)
def grafana_variables(
    service: DashboardService = Depends(get_dashboard_service),
    _user: User = Depends(require_permission(PermissionCode.DASHBOARD_VIEW)),
):
    return service.grafana_variables()
