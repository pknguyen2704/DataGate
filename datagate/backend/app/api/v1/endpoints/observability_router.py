from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.core.config import config
from app.db.session import get_db
from app.models import User
from app.rbac.permissions import PermissionCode
from app.schemas.dashboard_schema import GrafanaEmbedUrlOut, GrafanaVariablesOut, ManagedSchemaNodeOut
from app.services.dashboard_service import DashboardService

observability_router = APIRouter(prefix="/observability", tags=["Observability"])


def get_dashboard_service(db: Session = Depends(get_db)) -> DashboardService:
    return DashboardService(db)


@observability_router.get("/managed-tree", response_model=list[ManagedSchemaNodeOut])
def managed_tree(
    service: DashboardService = Depends(get_dashboard_service),
    _user: User = Depends(require_permission(PermissionCode.OBSERVABILITY_VIEW)),
):
    return service.managed_tree()


@observability_router.get("/grafana/variables", response_model=GrafanaVariablesOut)
def grafana_variables(
    service: DashboardService = Depends(get_dashboard_service),
    _user: User = Depends(require_permission(PermissionCode.OBSERVABILITY_VIEW)),
):
    return service.grafana_variables()


@observability_router.get("/grafana/embed-url", response_model=GrafanaEmbedUrlOut)
def grafana_embed_url(
    _user: User = Depends(require_permission(PermissionCode.OBSERVABILITY_VIEW)),
):
    base_url = getattr(config, "grafana_url", "http://localhost:3000")
    return {"url": f"{base_url}/d/datagate/data-quality"}
