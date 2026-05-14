from uuid import UUID
from fastapi import APIRouter, Depends, Body, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import require_permission
from app.db.session import get_db
from app.models import User
from app.rbac.permissions import PermissionCode
from app.schemas.lightgbm_schema import (
    LightGBMParameterCreate, LightGBMParameterOut, LightGBMParameterListOut,
    LightGBMParameterUpdate, LightGBMAUCOut, LightGBMAUCListOut, SHAPResultOut
)
from app.services.lightgbm_service import LightGBMService
from app.services.model_config_service import ModelConfigService

model_configs_router = APIRouter(prefix="/model-configs", tags=["Model Configurations"])

def get_lightgbm_service(db: Session = Depends(get_db)) -> LightGBMService:
    return LightGBMService(db)

def get_model_config_service(db: Session = Depends(get_db)) -> ModelConfigService:
    return ModelConfigService(db)


# Settings Endpoints (Slice 9)
@model_configs_router.get("", response_model=LightGBMParameterListOut)
def list_configs(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    service: ModelConfigService = Depends(get_model_config_service),
    _user: User = Depends(require_permission(PermissionCode.MODEL_CONFIG_VIEW))
):
    return service.list_configs(page=page, page_size=page_size)


@model_configs_router.get("/template")
def get_template(
    service: ModelConfigService = Depends(get_model_config_service),
    _user: User = Depends(require_permission(PermissionCode.MODEL_CONFIG_VIEW))
):
    return service.get_template()


@model_configs_router.post("/upload-json", response_model=LightGBMParameterOut)
def upload_json(
    table_id: UUID = Query(...),
    data: dict = Body(...),
    service: ModelConfigService = Depends(get_model_config_service),
    current_user: User = Depends(require_permission(PermissionCode.MODEL_CONFIG_MANAGE))
):
    return service.upload_json(str(table_id), data, str(current_user.id))


@model_configs_router.get("/{config_id}", response_model=LightGBMParameterOut)
def get_config(
    config_id: UUID,
    service: ModelConfigService = Depends(get_model_config_service),
    _user: User = Depends(require_permission(PermissionCode.MODEL_CONFIG_VIEW))
):
    return service.get_config_or_404(str(config_id))


@model_configs_router.post("", response_model=LightGBMParameterOut, status_code=status.HTTP_201_CREATED)
def create_config(
    data: LightGBMParameterCreate,
    service: ModelConfigService = Depends(get_model_config_service),
    current_user: User = Depends(require_permission(PermissionCode.MODEL_CONFIG_MANAGE))
):
    return service.create_config(data, str(current_user.id))


@model_configs_router.patch("/{config_id}", response_model=LightGBMParameterOut)
def update_config(
    config_id: UUID,
    data: LightGBMParameterUpdate,
    service: ModelConfigService = Depends(get_model_config_service),
    current_user: User = Depends(require_permission(PermissionCode.MODEL_CONFIG_MANAGE))
):
    return service.update_config(str(config_id), data, str(current_user.id))


@model_configs_router.delete("/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_config(
    config_id: UUID,
    service: ModelConfigService = Depends(get_model_config_service),
    _user: User = Depends(require_permission(PermissionCode.MODEL_CONFIG_MANAGE))
):
    service.delete_config(str(config_id))
    return None


# Observability Endpoints (Existing)
@model_configs_router.get("/auc-results", response_model=LightGBMAUCListOut)
def list_auc_results(
    table_id: UUID | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    service: LightGBMService = Depends(get_lightgbm_service), 
    _user: User = Depends(require_permission(PermissionCode.MODEL_CONFIG_VIEW))
):
    return service.list_auc_results(table_id=str(table_id) if table_id else None, page=page, page_size=page_size)

@model_configs_router.get("/auc-results/{auc_result_id}", response_model=LightGBMAUCOut)
def get_auc_result(auc_result_id: UUID, service: LightGBMService = Depends(get_lightgbm_service), _user: User = Depends(require_permission(PermissionCode.MODEL_CONFIG_VIEW))):
    return service.get_auc_result_or_404(str(auc_result_id))

@model_configs_router.get("/auc-results/{auc_result_id}/shap", response_model=list[SHAPResultOut])
def shap_results(auc_result_id: UUID, service: LightGBMService = Depends(get_lightgbm_service), _user: User = Depends(require_permission(PermissionCode.MODEL_CONFIG_VIEW))):
    return service.list_shap_results(str(auc_result_id))
