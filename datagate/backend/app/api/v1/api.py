from fastapi import APIRouter

from app.api.v1.endpoints.auth_router import auth_router
from app.api.v1.endpoints.anomaly_router import anomaly_router
from app.api.v1.endpoints.connection_router import connection_router
from app.api.v1.endpoints.home_router import home_router
from app.api.v1.endpoints.metric_router import metric_router
from app.api.v1.endpoints.model_config_router import lightgbm_router
from app.api.v1.endpoints.observability_router import observability_router
from app.api.v1.endpoints.quality_router import quality_router
from app.api.v1.endpoints.role_router import role_router
from app.api.v1.endpoints.rule_router import rules_router
from app.api.v1.endpoints.table_router import table_router
from app.api.v1.endpoints.user_router import user_router
from app.api.v1.endpoints.permission_router import permission_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(user_router)
api_router.include_router(role_router)
api_router.include_router(permission_router)
api_router.include_router(connection_router)
api_router.include_router(table_router)
api_router.include_router(rules_router)
api_router.include_router(home_router)
api_router.include_router(observability_router)
api_router.include_router(metric_router)
api_router.include_router(quality_router)
api_router.include_router(lightgbm_router)
api_router.include_router(anomaly_router)
