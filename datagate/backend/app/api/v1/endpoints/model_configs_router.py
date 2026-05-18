from uuid import UUID
from fastapi import APIRouter, Depends, Body, status, Query
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.db.session import get_db
from app.models import User
from app.rbac.permissions import PermissionCode
from app.schemas.model_schema import (
    ModelParameterCreate,
    ModelParameterOut,
    ModelParameterListOut,
    ModelParameterUpdate,
    AUCResultOut,
    AUCResultListOut,
    SHAPResultOut,
    ModelConfigCreate,
    ModelConfigListOut,
    ModelConfigOut,
    ModelConfigUpdate,
)
from app.services.model_config_service import ModelConfigService

model_configs_router = APIRouter(prefix="/model-configs", tags=["Model Configurations"])


def get_model_config_service(db: Session = Depends(get_db)) -> ModelConfigService:
    return ModelConfigService(db)


# Settings Endpoints (Slice 9)
@model_configs_router.get("", response_model=ModelParameterListOut)
def list_configs(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    service: ModelConfigService = Depends(get_model_config_service),
    _user: User = Depends(require_permission(PermissionCode.MODEL_CONFIG_VIEW)),
):
    return service.list_configs(page=page, page_size=page_size)


@model_configs_router.get("/template")
def get_template(
    service: ModelConfigService = Depends(get_model_config_service),
    _user: User = Depends(require_permission(PermissionCode.MODEL_CONFIG_VIEW)),
):
    return service.get_template()


@model_configs_router.post("/upload-json", response_model=ModelParameterOut)
def upload_json(
    table_id: UUID = Query(...),
    data: dict = Body(...),
    service: ModelConfigService = Depends(get_model_config_service),
    current_user: User = Depends(
        require_permission(PermissionCode.MODEL_CONFIG_UPDATE)
    ),
):
    return service.upload_json(str(table_id), data, str(current_user.id))


@model_configs_router.get("/configs", response_model=ModelConfigListOut)
def list_anomaly_configs(
    table_id: UUID | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    service: ModelConfigService = Depends(get_model_config_service),
    _user: User = Depends(require_permission(PermissionCode.MODEL_CONFIG_VIEW)),
):
    return service.list_anomaly_configs(
        table_id=str(table_id) if table_id else None,
        page=page,
        page_size=page_size,
    )


@model_configs_router.get("/configs/template")
def get_anomaly_config_template(
    service: ModelConfigService = Depends(get_model_config_service),
    _user: User = Depends(require_permission(PermissionCode.MODEL_CONFIG_VIEW)),
):
    return service.get_anomaly_config_template()


@model_configs_router.post("/configs/upload-json", response_model=ModelConfigOut)
def upload_anomaly_config_json(
    table_id: UUID = Query(...),
    data: dict = Body(...),
    service: ModelConfigService = Depends(get_model_config_service),
    current_user: User = Depends(
        require_permission(PermissionCode.MODEL_CONFIG_UPDATE)
    ),
):
    return service.upload_anomaly_config_json(str(table_id), data, str(current_user.id))


@model_configs_router.get("/configs/{config_id}", response_model=ModelConfigOut)
def get_anomaly_config(
    config_id: UUID,
    service: ModelConfigService = Depends(get_model_config_service),
    _user: User = Depends(require_permission(PermissionCode.MODEL_CONFIG_VIEW)),
):
    return service.get_anomaly_config_payload_or_404(str(config_id))


@model_configs_router.post(
    "/configs", response_model=ModelConfigOut, status_code=status.HTTP_201_CREATED
)
def create_anomaly_config(
    data: ModelConfigCreate,
    service: ModelConfigService = Depends(get_model_config_service),
    current_user: User = Depends(
        require_permission(PermissionCode.MODEL_CONFIG_UPDATE)
    ),
):
    return service.create_anomaly_config(data, str(current_user.id))


@model_configs_router.patch("/configs/{config_id}", response_model=ModelConfigOut)
def update_anomaly_config(
    config_id: UUID,
    data: ModelConfigUpdate,
    service: ModelConfigService = Depends(get_model_config_service),
    current_user: User = Depends(
        require_permission(PermissionCode.MODEL_CONFIG_UPDATE)
    ),
):
    return service.update_anomaly_config(str(config_id), data, str(current_user.id))


@model_configs_router.delete(
    "/configs/{config_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_anomaly_config(
    config_id: UUID,
    service: ModelConfigService = Depends(get_model_config_service),
    _user: User = Depends(require_permission(PermissionCode.MODEL_CONFIG_DELETE)),
):
    service.delete_anomaly_config(str(config_id))
    return None


# Observability Endpoints (Existing)
@model_configs_router.get("/auc-results", response_model=AUCResultListOut)
def list_auc_results(
    table_id: UUID | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    service: ModelConfigService = Depends(get_model_config_service),
    _user: User = Depends(require_permission(PermissionCode.MODEL_CONFIG_VIEW)),
):
    return service.list_auc_results(
        table_id=str(table_id) if table_id else None, page=page, page_size=page_size
    )


@model_configs_router.get("/auc-results/{auc_result_id}", response_model=AUCResultOut)
def get_auc_result(
    auc_result_id: UUID,
    service: ModelConfigService = Depends(get_model_config_service),
    _user: User = Depends(require_permission(PermissionCode.MODEL_CONFIG_VIEW)),
):
    return service.get_auc_result_or_404(str(auc_result_id))


@model_configs_router.get(
    "/auc-results/{auc_result_id}/shap", response_model=list[SHAPResultOut]
)
def shap_results(
    auc_result_id: UUID,
    service: ModelConfigService = Depends(get_model_config_service),
    _user: User = Depends(require_permission(PermissionCode.MODEL_CONFIG_VIEW)),
):
    return service.list_shap_results(str(auc_result_id))


@model_configs_router.get("/{config_id}", response_model=ModelParameterOut)
def get_config(
    config_id: UUID,
    service: ModelConfigService = Depends(get_model_config_service),
    _user: User = Depends(require_permission(PermissionCode.MODEL_CONFIG_VIEW)),
):
    return service.get_model_parameter_payload_or_404(str(config_id))


@model_configs_router.post(
    "", response_model=ModelParameterOut, status_code=status.HTTP_201_CREATED
)
def create_config(
    data: ModelParameterCreate,
    service: ModelConfigService = Depends(get_model_config_service),
    current_user: User = Depends(
        require_permission(PermissionCode.MODEL_CONFIG_UPDATE)
    ),
):
    return service.create_config(data, str(current_user.id))


@model_configs_router.patch("/{config_id}", response_model=ModelParameterOut)
def update_config(
    config_id: UUID,
    data: ModelParameterUpdate,
    service: ModelConfigService = Depends(get_model_config_service),
    current_user: User = Depends(
        require_permission(PermissionCode.MODEL_CONFIG_UPDATE)
    ),
):
    return service.update_config(str(config_id), data, str(current_user.id))


@model_configs_router.delete("/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_config(
    config_id: UUID,
    service: ModelConfigService = Depends(get_model_config_service),
    _user: User = Depends(require_permission(PermissionCode.MODEL_CONFIG_DELETE)),
):
    service.delete_config(str(config_id))
    return None
