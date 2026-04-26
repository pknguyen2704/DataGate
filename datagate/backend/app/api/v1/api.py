"""
API v1 router — registers all endpoint routers
"""
from fastapi import APIRouter
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.users import router as users_router
from app.api.v1.endpoints.roles import router as roles_router
from app.api.v1.endpoints.connections import router as connections_router
from app.api.v1.endpoints.tables import router as tables_router
from app.api.v1.endpoints.misc import (
    rules_router,
    alerts_router,
    jobs_router,
    dashboard_router,
    thresholds_router,
)

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(roles_router, prefix="/roles", tags=["Roles & Permissions"])
api_router.include_router(connections_router, prefix="/connections", tags=["Connections"])
api_router.include_router(tables_router, prefix="/tables", tags=["Tables"])
api_router.include_router(rules_router, prefix="/rules", tags=["Rules"])
api_router.include_router(alerts_router, prefix="/alerts", tags=["Alerts"])
api_router.include_router(jobs_router, prefix="/jobs", tags=["Jobs"])
api_router.include_router(thresholds_router, prefix="/thresholds", tags=["Thresholds"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
