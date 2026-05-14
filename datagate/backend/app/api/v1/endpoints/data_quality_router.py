from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from datetime import datetime
from uuid import UUID

from app.api.deps import require_permission
from app.db.session import get_db
from app.models import User
from app.rbac.permissions import PermissionCode
from app.schemas.data_quality_schema import (
    QualityResultOut, DataQualitySummary, MetadataResultDetail,
    ProfilingResultDetail, RuleResultDetail, AnomalyResultDetail, QualityResultListOut
)
from app.services.data_quality_service import DataQualityService

data_quality_router = APIRouter(prefix="/data-quality", tags=["Data Quality"])

def get_dq_service(db: Session = Depends(get_db)) -> DataQualityService:
    return DataQualityService(db)


@data_quality_router.get("/results", response_model=QualityResultListOut)
def list_results(
    table_id: UUID | None = Query(default=None),
    layer: str | None = Query(default=None),
    processing_date_hour: str | None = Query(default=None),
    status: str | None = Query(default=None),
    severity_level: str | None = Query(default=None),
    result_type: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    service: DataQualityService = Depends(get_dq_service),
    _user: User = Depends(require_permission(PermissionCode.QUALITY_VIEW)),
):
    pdh = None
    if processing_date_hour and processing_date_hour.strip():
        # Handle trailing Z if present, or just parse datetime-local format
        clean_pdh = processing_date_hour.replace("Z", "+00:00") if "Z" in processing_date_hour else processing_date_hour
        pdh = datetime.fromisoformat(clean_pdh)

    return service.list_results(
        str(table_id) if table_id else None,
        layer if layer and layer.strip() else None, 
        pdh, 
        status if status and status.strip() else None, 
        severity_level if severity_level and severity_level.strip() else None, 
        result_type if result_type and result_type.strip() else None, 
        page, 
        page_size
    )


@data_quality_router.get("/results/summary", response_model=DataQualitySummary)
def get_summary(
    table_id: UUID | None = Query(default=None),
    service: DataQualityService = Depends(get_dq_service),
    _user: User = Depends(require_permission(PermissionCode.QUALITY_VIEW)),
):
    return service.get_summary(str(table_id) if table_id else None)


@data_quality_router.get("/metadata-results/{result_id}", response_model=MetadataResultDetail)
def get_metadata_detail(
    result_id: UUID,
    service: DataQualityService = Depends(get_dq_service),
    _user: User = Depends(require_permission(PermissionCode.QUALITY_VIEW)),
):
    return service.get_metadata_detail(str(result_id))


@data_quality_router.patch("/metadata-results/{result_id}/resolve")
def resolve_metadata(
    result_id: UUID,
    service: DataQualityService = Depends(get_dq_service),
    current_user: User = Depends(require_permission(PermissionCode.QUALITY_RUN)), # Mapping resolve to quality:run/update
):
    return service.resolve_result("metadata", str(result_id), str(current_user.id))


@data_quality_router.get("/profiling-results/{result_id}", response_model=ProfilingResultDetail)
def get_profiling_detail(
    result_id: UUID,
    service: DataQualityService = Depends(get_dq_service),
    _user: User = Depends(require_permission(PermissionCode.QUALITY_VIEW)),
):
    return service.get_profiling_detail(str(result_id))


@data_quality_router.patch("/profiling-results/{result_id}/resolve")
def resolve_profiling(
    result_id: UUID,
    service: DataQualityService = Depends(get_dq_service),
    current_user: User = Depends(require_permission(PermissionCode.QUALITY_RUN)),
):
    return service.resolve_result("profiling", str(result_id), str(current_user.id))


@data_quality_router.get("/rule-results/{result_id}", response_model=RuleResultDetail)
def get_rule_detail(
    result_id: UUID,
    service: DataQualityService = Depends(get_dq_service),
    _user: User = Depends(require_permission(PermissionCode.QUALITY_VIEW)),
):
    return service.get_rule_detail(str(result_id))


@data_quality_router.patch("/rule-results/{result_id}/resolve")
def resolve_rule(
    result_id: UUID,
    service: DataQualityService = Depends(get_dq_service),
    current_user: User = Depends(require_permission(PermissionCode.QUALITY_RUN)),
):
    return service.resolve_result("rule", str(result_id), str(current_user.id))


@data_quality_router.get("/anomaly-results/{result_id}", response_model=AnomalyResultDetail)
def get_anomaly_detail(
    result_id: UUID,
    service: DataQualityService = Depends(get_dq_service),
    _user: User = Depends(require_permission(PermissionCode.QUALITY_VIEW)),
):
    return service.get_anomaly_detail(str(result_id))


@data_quality_router.patch("/anomaly-results/{result_id}/resolve")
def resolve_anomaly(
    result_id: UUID,
    service: DataQualityService = Depends(get_dq_service),
    current_user: User = Depends(require_permission(PermissionCode.QUALITY_RUN)),
):
    return service.resolve_result("anomaly", str(result_id), str(current_user.id))
