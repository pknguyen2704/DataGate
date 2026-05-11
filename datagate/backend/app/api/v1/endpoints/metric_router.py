from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.db.session import get_db
from app.models import User
from app.rbac.permissions import PermissionCode
from app.schemas.lightgbm_schema import LightGBMAUCManualThresholdCreate, LightGBMAUCManualThresholdOut, LightGBMAUCManualThresholdUpdate
from app.schemas.metric_schema import BatchTableMetadataManualThresholdCreate, BatchTableMetadataManualThresholdOut, BatchTableMetadataManualThresholdUpdate, BatchTableProfilingManualThresholdCreate, BatchTableProfilingManualThresholdOut, BatchTableProfilingManualThresholdUpdate
from app.services.metric_service import MetricService


metric_router = APIRouter(prefix="/metrics", tags=["Metrics"])


def get_metric_service(db: Session = Depends(get_db)) -> MetricService:
    return MetricService(db)


@metric_router.get("/metadata-thresholds", response_model=list[BatchTableMetadataManualThresholdOut])
def list_metadata_thresholds(service: MetricService = Depends(get_metric_service), _user: User = Depends(require_permission(PermissionCode.THRESHOLD_VIEW))):
    return service.list_thresholds("metadata")


@metric_router.post("/metadata-thresholds", response_model=BatchTableMetadataManualThresholdOut, status_code=status.HTTP_201_CREATED)
def create_metadata_threshold(data: BatchTableMetadataManualThresholdCreate, service: MetricService = Depends(get_metric_service), current_user: User = Depends(require_permission(PermissionCode.THRESHOLD_CREATE))):
    return service.create_threshold("metadata", data, str(current_user.id))


@metric_router.put("/metadata-thresholds/{threshold_id}", response_model=BatchTableMetadataManualThresholdOut)
def update_metadata_threshold(threshold_id: UUID, data: BatchTableMetadataManualThresholdUpdate, service: MetricService = Depends(get_metric_service), current_user: User = Depends(require_permission(PermissionCode.THRESHOLD_UPDATE))):
    return service.update_threshold("metadata", str(threshold_id), data, str(current_user.id))


@metric_router.delete("/metadata-thresholds/{threshold_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_metadata_threshold(threshold_id: UUID, service: MetricService = Depends(get_metric_service), _user: User = Depends(require_permission(PermissionCode.THRESHOLD_DELETE))):
    service.delete_threshold("metadata", str(threshold_id))
    return None


@metric_router.patch("/metadata-thresholds/{threshold_id}/activate", response_model=BatchTableMetadataManualThresholdOut)
def activate_metadata_threshold(threshold_id: UUID, service: MetricService = Depends(get_metric_service), current_user: User = Depends(require_permission(PermissionCode.THRESHOLD_UPDATE))):
    return service.set_active("metadata", str(threshold_id), True, str(current_user.id))


@metric_router.patch("/metadata-thresholds/{threshold_id}/deactivate", response_model=BatchTableMetadataManualThresholdOut)
def deactivate_metadata_threshold(threshold_id: UUID, service: MetricService = Depends(get_metric_service), current_user: User = Depends(require_permission(PermissionCode.THRESHOLD_UPDATE))):
    return service.set_active("metadata", str(threshold_id), False, str(current_user.id))


@metric_router.get("/profiling-thresholds", response_model=list[BatchTableProfilingManualThresholdOut])
def list_profiling_thresholds(service: MetricService = Depends(get_metric_service), _user: User = Depends(require_permission(PermissionCode.THRESHOLD_VIEW))):
    return service.list_thresholds("profiling")


@metric_router.post("/profiling-thresholds", response_model=BatchTableProfilingManualThresholdOut, status_code=status.HTTP_201_CREATED)
def create_profiling_threshold(data: BatchTableProfilingManualThresholdCreate, service: MetricService = Depends(get_metric_service), current_user: User = Depends(require_permission(PermissionCode.THRESHOLD_CREATE))):
    return service.create_threshold("profiling", data, str(current_user.id))


@metric_router.put("/profiling-thresholds/{threshold_id}", response_model=BatchTableProfilingManualThresholdOut)
def update_profiling_threshold(threshold_id: UUID, data: BatchTableProfilingManualThresholdUpdate, service: MetricService = Depends(get_metric_service), current_user: User = Depends(require_permission(PermissionCode.THRESHOLD_UPDATE))):
    return service.update_threshold("profiling", str(threshold_id), data, str(current_user.id))


@metric_router.delete("/profiling-thresholds/{threshold_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_profiling_threshold(threshold_id: UUID, service: MetricService = Depends(get_metric_service), _user: User = Depends(require_permission(PermissionCode.THRESHOLD_DELETE))):
    service.delete_threshold("profiling", str(threshold_id))
    return None


@metric_router.patch("/profiling-thresholds/{threshold_id}/activate", response_model=BatchTableProfilingManualThresholdOut)
def activate_profiling_threshold(threshold_id: UUID, service: MetricService = Depends(get_metric_service), current_user: User = Depends(require_permission(PermissionCode.THRESHOLD_UPDATE))):
    return service.set_active("profiling", str(threshold_id), True, str(current_user.id))


@metric_router.patch("/profiling-thresholds/{threshold_id}/deactivate", response_model=BatchTableProfilingManualThresholdOut)
def deactivate_profiling_threshold(threshold_id: UUID, service: MetricService = Depends(get_metric_service), current_user: User = Depends(require_permission(PermissionCode.THRESHOLD_UPDATE))):
    return service.set_active("profiling", str(threshold_id), False, str(current_user.id))


@metric_router.get("/auc-thresholds", response_model=list[LightGBMAUCManualThresholdOut])
def list_auc_thresholds(service: MetricService = Depends(get_metric_service), _user: User = Depends(require_permission(PermissionCode.THRESHOLD_VIEW))):
    return service.list_thresholds("auc")


@metric_router.post("/auc-thresholds", response_model=LightGBMAUCManualThresholdOut, status_code=status.HTTP_201_CREATED)
def create_auc_threshold(data: LightGBMAUCManualThresholdCreate, service: MetricService = Depends(get_metric_service), current_user: User = Depends(require_permission(PermissionCode.THRESHOLD_CREATE))):
    return service.create_threshold("auc", data, str(current_user.id))


@metric_router.put("/auc-thresholds/{threshold_id}", response_model=LightGBMAUCManualThresholdOut)
def update_auc_threshold(threshold_id: UUID, data: LightGBMAUCManualThresholdUpdate, service: MetricService = Depends(get_metric_service), current_user: User = Depends(require_permission(PermissionCode.THRESHOLD_UPDATE))):
    return service.update_threshold("auc", str(threshold_id), data, str(current_user.id))


@metric_router.delete("/auc-thresholds/{threshold_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_auc_threshold(threshold_id: UUID, service: MetricService = Depends(get_metric_service), _user: User = Depends(require_permission(PermissionCode.THRESHOLD_DELETE))):
    service.delete_threshold("auc", str(threshold_id))
    return None
