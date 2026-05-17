from fastapi import APIRouter

from app.api.v1.endpoints.auth_router import auth_router
from app.api.v1.endpoints.data_assets_router import data_assets_router
from app.api.v1.endpoints.data_quality_router import data_quality_router
from app.api.v1.endpoints.home_router import home_router
from app.api.v1.endpoints.lab_router import lab_router
from app.api.v1.endpoints.metrics_router import metrics_router
from app.api.v1.endpoints.observability_router import observability_router
from app.api.v1.endpoints.rules_router import rules_router
from app.api.v1.endpoints.settings_router import settings_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(home_router)
api_router.include_router(lab_router)
api_router.include_router(data_assets_router)
api_router.include_router(observability_router)
api_router.include_router(metrics_router)
api_router.include_router(rules_router)
api_router.include_router(data_quality_router)
api_router.include_router(settings_router)
