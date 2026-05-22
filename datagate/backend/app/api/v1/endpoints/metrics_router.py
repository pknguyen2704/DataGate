from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_permission
from app.db.session import get_db
from app.models import User
from app.rbac.permissions import PermissionCode
from app.schemas.metrics_schema import (
    AnomalyThresholdCreate,
    AnomalyThresholdListOut,
    AnomalyThresholdOut,
    AnomalyThresholdUpdate,
    MetadataThresholdCreate,
    MetadataThresholdListOut,
    MetadataThresholdOut,
    MetadataThresholdUpdate,
    ProfilingThresholdCreate,
    ProfilingThresholdListOut,
    ProfilingThresholdOut,
    ProfilingThresholdUpdate,
)
from app.services.metrics_service import MetricsService

metrics_router = APIRouter(prefix="/metrics", tags=["Metrics"])


def get_metrics_service(db: Session = Depends(get_db)) -> MetricsService:
    return MetricsService(db)


@metrics_router.get("/metadata-thresholds", response_model=MetadataThresholdListOut)
def list_metadata_thresholds(
    table_id: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    service: MetricsService = Depends(get_metrics_service),
    _user: User = Depends(require_permission(PermissionCode.THRESHOLD_MANAGE)),
):
    return service.list_metadata_thresholds(
        table_id=table_id, page=page, page_size=page_size
    )


@metrics_router.post(
    "/metadata-thresholds",
    response_model=MetadataThresholdOut,
    status_code=status.HTTP_201_CREATED,
)
def create_metadata_threshold(
    data: MetadataThresholdCreate,
    service: MetricsService = Depends(get_metrics_service),
    current_user: User = Depends(require_permission(PermissionCode.THRESHOLD_MANAGE)),
):
    return service.create_metadata_threshold(data, str(current_user.id))


@metrics_router.get(
    "/metadata-thresholds/{threshold_id}", response_model=MetadataThresholdOut
)
def get_metadata_threshold(
    threshold_id: UUID,
    service: MetricsService = Depends(get_metrics_service),
    _user: User = Depends(require_permission(PermissionCode.THRESHOLD_MANAGE)),
):
    return service.get_metadata_threshold(str(threshold_id))


@metrics_router.patch(
    "/metadata-thresholds/{threshold_id}", response_model=MetadataThresholdOut
)
def update_metadata_threshold(
    threshold_id: UUID,
    data: MetadataThresholdUpdate,
    service: MetricsService = Depends(get_metrics_service),
    current_user: User = Depends(require_permission(PermissionCode.THRESHOLD_MANAGE)),
):
    return service.update_metadata_threshold(
        str(threshold_id), data, str(current_user.id)
    )


@metrics_router.delete(
    "/metadata-thresholds/{threshold_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_metadata_threshold(
    threshold_id: UUID,
    service: MetricsService = Depends(get_metrics_service),
    _user: User = Depends(require_permission(PermissionCode.THRESHOLD_MANAGE)),
):
    service.delete_metadata_threshold(str(threshold_id))
    return None


@metrics_router.get("/profiling-thresholds", response_model=ProfilingThresholdListOut)
def list_profiling_thresholds(
    table_id: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    service: MetricsService = Depends(get_metrics_service),
    _user: User = Depends(require_permission(PermissionCode.THRESHOLD_MANAGE)),
):
    return service.list_profiling_thresholds(
        table_id=table_id, page=page, page_size=page_size
    )


@metrics_router.post(
    "/profiling-thresholds",
    response_model=ProfilingThresholdOut,
    status_code=status.HTTP_201_CREATED,
)
def create_profiling_threshold(
    data: ProfilingThresholdCreate,
    service: MetricsService = Depends(get_metrics_service),
    current_user: User = Depends(require_permission(PermissionCode.THRESHOLD_MANAGE)),
):
    return service.create_profiling_threshold(data, str(current_user.id))


@metrics_router.get(
    "/profiling-thresholds/{threshold_id}", response_model=ProfilingThresholdOut
)
def get_profiling_threshold(
    threshold_id: UUID,
    service: MetricsService = Depends(get_metrics_service),
    _user: User = Depends(require_permission(PermissionCode.THRESHOLD_MANAGE)),
):
    return service.get_profiling_threshold(str(threshold_id))


@metrics_router.patch(
    "/profiling-thresholds/{threshold_id}", response_model=ProfilingThresholdOut
)
def update_profiling_threshold(
    threshold_id: UUID,
    data: ProfilingThresholdUpdate,
    service: MetricsService = Depends(get_metrics_service),
    current_user: User = Depends(require_permission(PermissionCode.THRESHOLD_MANAGE)),
):
    return service.update_profiling_threshold(
        str(threshold_id), data, str(current_user.id)
    )


@metrics_router.delete(
    "/profiling-thresholds/{threshold_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_profiling_threshold(
    threshold_id: UUID,
    service: MetricsService = Depends(get_metrics_service),
    _user: User = Depends(require_permission(PermissionCode.THRESHOLD_MANAGE)),
):
    service.delete_profiling_threshold(str(threshold_id))
    return None


@metrics_router.get("/anomaly-thresholds", response_model=AnomalyThresholdListOut)
def list_anomaly_thresholds(
    table_id: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    service: MetricsService = Depends(get_metrics_service),
    _user: User = Depends(require_permission(PermissionCode.THRESHOLD_MANAGE)),
):
    return service.list_anomaly_thresholds(
        table_id=table_id, page=page, page_size=page_size
    )


@metrics_router.post(
    "/anomaly-thresholds",
    response_model=AnomalyThresholdOut,
    status_code=status.HTTP_201_CREATED,
)
def create_anomaly_threshold(
    data: AnomalyThresholdCreate,
    service: MetricsService = Depends(get_metrics_service),
    current_user: User = Depends(require_permission(PermissionCode.THRESHOLD_MANAGE)),
):
    return service.create_anomaly_threshold(data, str(current_user.id))


@metrics_router.get(
    "/anomaly-thresholds/{threshold_id}", response_model=AnomalyThresholdOut
)
def get_anomaly_threshold(
    threshold_id: UUID,
    service: MetricsService = Depends(get_metrics_service),
    _user: User = Depends(require_permission(PermissionCode.THRESHOLD_MANAGE)),
):
    return service.get_anomaly_threshold(str(threshold_id))


@metrics_router.patch(
    "/anomaly-thresholds/{threshold_id}", response_model=AnomalyThresholdOut
)
def update_anomaly_threshold(
    threshold_id: UUID,
    data: AnomalyThresholdUpdate,
    service: MetricsService = Depends(get_metrics_service),
    current_user: User = Depends(require_permission(PermissionCode.THRESHOLD_MANAGE)),
):
    return service.update_anomaly_threshold(
        str(threshold_id), data, str(current_user.id)
    )


@metrics_router.delete(
    "/anomaly-thresholds/{threshold_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_anomaly_threshold(
    threshold_id: UUID,
    service: MetricsService = Depends(get_metrics_service),
    _user: User = Depends(require_permission(PermissionCode.THRESHOLD_MANAGE)),
):
    service.delete_anomaly_threshold(str(threshold_id))
    return None
