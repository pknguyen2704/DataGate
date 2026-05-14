from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.db.session import get_db
from app.models import LightGBMAUCVerify, User
from app.rbac.permissions import PermissionCode
from app.schemas.dashboard_schema import QualityResultOut
from app.schemas.lightgbm_schema import LightGBMAUCOut, SHAPResultOut
from app.services.lightgbm_service import LightGBMService


anomaly_router = APIRouter(prefix="/anomaly", tags=["Anomaly"])


def get_lightgbm_service(db: Session = Depends(get_db)) -> LightGBMService:
    return LightGBMService(db)


@anomaly_router.get("/auc-results", response_model=list[LightGBMAUCOut])
def list_auc_results(service: LightGBMService = Depends(get_lightgbm_service), _user: User = Depends(require_permission(PermissionCode.QUALITY_VIEW))):
    return service.list_auc_results()


@anomaly_router.get("/auc-results/{auc_result_id}", response_model=LightGBMAUCOut)
def get_auc_result(auc_result_id: UUID, service: LightGBMService = Depends(get_lightgbm_service), _user: User = Depends(require_permission(PermissionCode.QUALITY_VIEW))):
    return service.get_auc_result_or_404(str(auc_result_id))


@anomaly_router.get("/tables/{table_id}/auc-timeline", response_model=list[LightGBMAUCOut])
def auc_timeline(table_id: UUID, service: LightGBMService = Depends(get_lightgbm_service), _user: User = Depends(require_permission(PermissionCode.QUALITY_VIEW))):
    return service.list_auc_results(str(table_id))


@anomaly_router.get("/auc-results/{auc_result_id}/shap", response_model=list[SHAPResultOut])
def shap_results(auc_result_id: UUID, service: LightGBMService = Depends(get_lightgbm_service), _user: User = Depends(require_permission(PermissionCode.QUALITY_VIEW))):
    return service.list_shap_results(str(auc_result_id))


@anomaly_router.get("/verify-results", response_model=list[QualityResultOut])
def verify_results(db: Session = Depends(get_db), _user: User = Depends(require_permission(PermissionCode.QUALITY_VIEW))):
    rows = db.query(LightGBMAUCVerify).order_by(LightGBMAUCVerify.processing_date_hour.desc()).limit(200).all()
    return [{"id": row.id, "result_type": "anomaly", "status": row.status, "severity_level": row.severity_level, "is_resolved": row.is_resolved, "processing_date_hour": row.processing_date_hour} for row in rows]


@anomaly_router.patch("/verify-results/{verify_id}/resolve", response_model=QualityResultOut)
def resolve_verify_result(verify_id: UUID, db: Session = Depends(get_db), _user: User = Depends(require_permission(PermissionCode.QUALITY_RESOLVE))):
    row = db.query(LightGBMAUCVerify).filter(LightGBMAUCVerify.id == str(verify_id)).first()
    row.is_resolved = True
    db.commit()
    db.refresh(row)
    return {"id": row.id, "result_type": "anomaly", "status": row.status, "severity_level": row.severity_level, "is_resolved": row.is_resolved, "processing_date_hour": row.processing_date_hour}


@anomaly_router.patch("/verify-results/{verify_id}/unresolve", response_model=QualityResultOut)
def unresolve_verify_result(verify_id: UUID, db: Session = Depends(get_db), _user: User = Depends(require_permission(PermissionCode.QUALITY_RESOLVE))):
    row = db.query(LightGBMAUCVerify).filter(LightGBMAUCVerify.id == str(verify_id)).first()
    row.is_resolved = False
    db.commit()
    db.refresh(row)
    return {"id": row.id, "result_type": "anomaly", "status": row.status, "severity_level": row.severity_level, "is_resolved": row.is_resolved, "processing_date_hour": row.processing_date_hour}
