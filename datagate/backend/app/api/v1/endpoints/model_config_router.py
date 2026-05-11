from uuid import UUID
from fastapi import APIRouter, Depends, Body, status
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.db.session import get_db
from app.models import User
from app.rbac.permissions import PermissionCode
from app.schemas.lightgbm_schema import LightGBMParameterCreate, LightGBMParameterOut, LightGBMParameterUpdate, LightGBMAUCOut, SHAPResultOut
from app.services.lightgbm_service import LightGBMService


lightgbm_router = APIRouter(prefix="/lightgbm", tags=["LightGBM"])


def get_lightgbm_service(db: Session = Depends(get_db)) -> LightGBMService:
    return LightGBMService(db)


@lightgbm_router.get("/parameters", response_model=list[LightGBMParameterOut])
def list_parameters(service: LightGBMService = Depends(get_lightgbm_service), _user: User = Depends(require_permission(PermissionCode.ANOMALY_VIEW))):
    return service.list_parameters()


@lightgbm_router.post("/parameters", response_model=LightGBMParameterOut, status_code=status.HTTP_201_CREATED)
def create_parameter(data: LightGBMParameterCreate, service: LightGBMService = Depends(get_lightgbm_service), current_user: User = Depends(require_permission(PermissionCode.ANOMALY_RUN))):
    return service.create_parameter(data, str(current_user.id))


@lightgbm_router.post("/parameters/validate-json")
def validate_json(data: dict = Body(...), service: LightGBMService = Depends(get_lightgbm_service), _user: User = Depends(require_permission(PermissionCode.ANOMALY_VIEW))):
    return service.validate_json(data)


@lightgbm_router.post("/parameters/import-json", response_model=LightGBMParameterOut, status_code=status.HTTP_201_CREATED)
def import_json(data: LightGBMParameterCreate, service: LightGBMService = Depends(get_lightgbm_service), current_user: User = Depends(require_permission(PermissionCode.ANOMALY_RUN))):
    return service.import_json(data, str(current_user.id))


@lightgbm_router.get("/parameters/{parameter_id}", response_model=LightGBMParameterOut)
def get_parameter(parameter_id: UUID, service: LightGBMService = Depends(get_lightgbm_service), _user: User = Depends(require_permission(PermissionCode.ANOMALY_VIEW))):
    return service.get_parameter_or_404(str(parameter_id))


@lightgbm_router.put("/parameters/{parameter_id}", response_model=LightGBMParameterOut)
def update_parameter(parameter_id: UUID, data: LightGBMParameterUpdate, service: LightGBMService = Depends(get_lightgbm_service), current_user: User = Depends(require_permission(PermissionCode.ANOMALY_RUN))):
    return service.update_parameter(str(parameter_id), data, str(current_user.id))


@lightgbm_router.delete("/parameters/{parameter_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_parameter(parameter_id: UUID, service: LightGBMService = Depends(get_lightgbm_service), _user: User = Depends(require_permission(PermissionCode.ANOMALY_RUN))):
    service.delete_parameter(str(parameter_id))
    return None


@lightgbm_router.get("/tables/{table_id}/parameters", response_model=list[LightGBMParameterOut])
def list_table_parameters(table_id: UUID, service: LightGBMService = Depends(get_lightgbm_service), _user: User = Depends(require_permission(PermissionCode.ANOMALY_VIEW))):
    return service.list_parameters(str(table_id))


@lightgbm_router.get("/auc-results", response_model=list[LightGBMAUCOut])
def list_auc_results(service: LightGBMService = Depends(get_lightgbm_service), _user: User = Depends(require_permission(PermissionCode.ANOMALY_VIEW))):
    return service.list_auc_results()


@lightgbm_router.get("/auc-results/{auc_result_id}", response_model=LightGBMAUCOut)
def get_auc_result(auc_result_id: UUID, service: LightGBMService = Depends(get_lightgbm_service), _user: User = Depends(require_permission(PermissionCode.ANOMALY_VIEW))):
    return service.get_auc_result_or_404(str(auc_result_id))


@lightgbm_router.get("/tables/{table_id}/auc-timeline", response_model=list[LightGBMAUCOut])
def auc_timeline(table_id: UUID, service: LightGBMService = Depends(get_lightgbm_service), _user: User = Depends(require_permission(PermissionCode.ANOMALY_VIEW))):
    return service.list_auc_results(str(table_id))


@lightgbm_router.get("/auc-results/{auc_result_id}/shap", response_model=list[SHAPResultOut])
def shap_results(auc_result_id: UUID, service: LightGBMService = Depends(get_lightgbm_service), _user: User = Depends(require_permission(PermissionCode.ANOMALY_VIEW))):
    return service.list_shap_results(str(auc_result_id))
