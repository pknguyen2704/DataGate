from uuid import UUID
from fastapi import APIRouter, Depends, Body, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_permission
from app.db.session import get_db
from app.models import User
from app.rbac.permissions import PermissionCode
from app.schemas.anomaly_schema import (
    ModelParameterCreate,
    ModelParameterOut,
    ModelParameterListOut,
    ModelParameterUpdate,
    AUCResultOut,
    AUCResultListOut,
    SHAPResultOut,
    AnomalyConfigCreate,
    AnomalyConfigListOut,
    AnomalyConfigOut,
    AnomalyConfigUpdate,
)
from app.services.anomaly_config_service import AnomalyConfigService

anomaly_configs_router = APIRouter(prefix="/anomaly-configs", tags=["Model Configurations"])


def get_anomaly_config_service(db: Session = Depends(get_db)) -> AnomalyConfigService:
    return AnomalyConfigService(db)


# Settings Endpoints (Slice 9)
@anomaly_configs_router.get("", response_model=ModelParameterListOut)
def list_configs(
    table_id: UUID | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    service: AnomalyConfigService = Depends(get_anomaly_config_service),
    _user: User = Depends(require_permission(PermissionCode.ANOMALY_CONFIG_MANAGE)),
):
    return service.list_configs(
        table_id=str(table_id) if table_id else None,
        page=page,
        page_size=page_size,
    )


@anomaly_configs_router.get("/template")
def get_template(
    service: AnomalyConfigService = Depends(get_anomaly_config_service),
    _user: User = Depends(require_permission(PermissionCode.ANOMALY_CONFIG_MANAGE)),
):
    return service.get_template()


@anomaly_configs_router.post("/upload-json", response_model=ModelParameterOut)
def upload_json(
    table_id: UUID = Query(...),
    data: dict = Body(...),
    service: AnomalyConfigService = Depends(get_anomaly_config_service),
    current_user: User = Depends(
        require_permission(PermissionCode.ANOMALY_CONFIG_MANAGE)
    ),
):
    return service.upload_json(str(table_id), data, str(current_user.id))


@anomaly_configs_router.get("/configs", response_model=AnomalyConfigListOut)
def list_anomaly_configs(
    table_id: UUID | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    service: AnomalyConfigService = Depends(get_anomaly_config_service),
    _user: User = Depends(require_permission(PermissionCode.ANOMALY_CONFIG_MANAGE)),
):
    return service.list_anomaly_configs(
        table_id=str(table_id) if table_id else None,
        page=page,
        page_size=page_size,
    )


@anomaly_configs_router.get("/configs/template")
def get_anomaly_config_template(
    service: AnomalyConfigService = Depends(get_anomaly_config_service),
    _user: User = Depends(require_permission(PermissionCode.ANOMALY_CONFIG_MANAGE)),
):
    return service.get_anomaly_config_template()


@anomaly_configs_router.post("/configs/upload-json", response_model=AnomalyConfigOut)
def upload_anomaly_config_json(
    table_id: UUID = Query(...),
    data: dict = Body(...),
    service: AnomalyConfigService = Depends(get_anomaly_config_service),
    current_user: User = Depends(
        require_permission(PermissionCode.ANOMALY_CONFIG_MANAGE)
    ),
):
    return service.upload_anomaly_config_json(str(table_id), data, str(current_user.id))


@anomaly_configs_router.get("/configs/{config_id}", response_model=AnomalyConfigOut)
def get_anomaly_config(
    config_id: UUID,
    service: AnomalyConfigService = Depends(get_anomaly_config_service),
    _user: User = Depends(require_permission(PermissionCode.ANOMALY_CONFIG_MANAGE)),
):
    return service.get_anomaly_config_payload_or_404(str(config_id))


@anomaly_configs_router.post(
    "/configs", response_model=AnomalyConfigOut, status_code=status.HTTP_201_CREATED
)
def create_anomaly_config(
    data: AnomalyConfigCreate,
    service: AnomalyConfigService = Depends(get_anomaly_config_service),
    current_user: User = Depends(
        require_permission(PermissionCode.ANOMALY_CONFIG_MANAGE)
    ),
):
    return service.create_anomaly_config(data, str(current_user.id))


@anomaly_configs_router.patch("/configs/{config_id}", response_model=AnomalyConfigOut)
def update_anomaly_config(
    config_id: UUID,
    data: AnomalyConfigUpdate,
    service: AnomalyConfigService = Depends(get_anomaly_config_service),
    current_user: User = Depends(
        require_permission(PermissionCode.ANOMALY_CONFIG_MANAGE)
    ),
):
    return service.update_anomaly_config(str(config_id), data, str(current_user.id))


@anomaly_configs_router.delete(
    "/configs/{config_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_anomaly_config(
    config_id: UUID,
    service: AnomalyConfigService = Depends(get_anomaly_config_service),
    _user: User = Depends(require_permission(PermissionCode.ANOMALY_CONFIG_MANAGE)),
):
    service.delete_anomaly_config(str(config_id))
    return None


# Observability Endpoints (Existing)
@anomaly_configs_router.get("/auc-results", response_model=AUCResultListOut)
def list_auc_results(
    table_id: UUID | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    service: AnomalyConfigService = Depends(get_anomaly_config_service),
    _user: User = Depends(get_current_user),
):
    return service.list_auc_results(
        table_id=str(table_id) if table_id else None, page=page, page_size=page_size
    )


@anomaly_configs_router.get("/auc-results/{anomaly_result_id}", response_model=AUCResultOut)
def get_auc_result(
    anomaly_result_id: UUID,
    service: AnomalyConfigService = Depends(get_anomaly_config_service),
    _user: User = Depends(get_current_user),
):
    return service.get_auc_result_or_404(str(anomaly_result_id))


@anomaly_configs_router.get(
    "/auc-results/{anomaly_result_id}/shap", response_model=list[SHAPResultOut]
)
def shap_results(
    anomaly_result_id: UUID,
    service: AnomalyConfigService = Depends(get_anomaly_config_service),
    _user: User = Depends(get_current_user),
):
    return service.list_shap_results(str(anomaly_result_id))


@anomaly_configs_router.get("/{config_id}", response_model=ModelParameterOut)
def get_config(
    config_id: UUID,
    service: AnomalyConfigService = Depends(get_anomaly_config_service),
    _user: User = Depends(require_permission(PermissionCode.ANOMALY_CONFIG_MANAGE)),
):
    return service.get_model_parameter_payload_or_404(str(config_id))


@anomaly_configs_router.post(
    "", response_model=ModelParameterOut, status_code=status.HTTP_201_CREATED
)
def create_config(
    data: ModelParameterCreate,
    service: AnomalyConfigService = Depends(get_anomaly_config_service),
    current_user: User = Depends(
        require_permission(PermissionCode.ANOMALY_CONFIG_MANAGE)
    ),
):
    return service.create_config(data, str(current_user.id))


@anomaly_configs_router.patch("/{config_id}", response_model=ModelParameterOut)
def update_config(
    config_id: UUID,
    data: ModelParameterUpdate,
    service: AnomalyConfigService = Depends(get_anomaly_config_service),
    current_user: User = Depends(
        require_permission(PermissionCode.ANOMALY_CONFIG_MANAGE)
    ),
):
    return service.update_config(str(config_id), data, str(current_user.id))


@anomaly_configs_router.delete("/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_config(
    config_id: UUID,
    service: AnomalyConfigService = Depends(get_anomaly_config_service),
    _user: User = Depends(require_permission(PermissionCode.ANOMALY_CONFIG_MANAGE)),
):
    service.delete_config(str(config_id))
    return None
