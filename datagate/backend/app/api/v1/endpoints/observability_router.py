from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.db.session import get_db
from app.models import User
from app.rbac.permissions import PermissionCode
from app.schemas.observability_schema import (
    ObservabilityEmbedUrlOut,
    ObservabilityVariablesOut,
    ManagedSchemaNodeOut,
    TimeRangeOut,
)
from app.services.observability_service import ObservabilityService

observability_router = APIRouter(prefix="/observability", tags=["Observability"])


def get_observability_service(db: Session = Depends(get_db)) -> ObservabilityService:
    return ObservabilityService(db)


@observability_router.get(
    "/tables/{table_id}/default-time-range", response_model=TimeRangeOut
)
def default_time_range(
    table_id: UUID,
    service: ObservabilityService = Depends(get_observability_service),
    _user: User = Depends(require_permission(PermissionCode.HOME_VIEW)),
):
    return service.get_default_time_range(str(table_id))


@observability_router.get(
    "/tables/{table_id}/observability", response_model=ObservabilityEmbedUrlOut
)
def observability_dashboard(
    table_id: UUID,
    from_time: datetime | None = Query(default=None),
    to_time: datetime | None = Query(default=None),
    service: ObservabilityService = Depends(get_observability_service),
    _user: User = Depends(require_permission(PermissionCode.HOME_VIEW)),
):
    url = service.get_observability_dashboard_url(
        table_id=str(table_id), from_time=from_time, to_time=to_time
    )
    return {"url": url}


@observability_router.get("/managed-tree", response_model=list[ManagedSchemaNodeOut])
def managed_tree(
    service: ObservabilityService = Depends(get_observability_service),
    _user: User = Depends(require_permission(PermissionCode.HOME_VIEW)),
):
    return service.managed_tree()


@observability_router.get("/variables", response_model=ObservabilityVariablesOut)
def observability_variables(
    service: ObservabilityService = Depends(get_observability_service),
    _user: User = Depends(require_permission(PermissionCode.HOME_VIEW)),
):
    return service.observability_variables()
