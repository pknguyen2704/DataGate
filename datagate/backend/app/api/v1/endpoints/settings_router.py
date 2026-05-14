from fastapi import APIRouter
from app.api.v1.endpoints.connections_router import connections_router
from app.api.v1.endpoints.model_configs_router import model_configs_router
from app.api.v1.endpoints.users_router import users_router
from app.api.v1.endpoints.roles_router import roles_router
from app.api.v1.endpoints.permission_router import permission_router

settings_router = APIRouter(prefix="/settings", tags=["Settings"])

settings_router.include_router(connections_router)
settings_router.include_router(model_configs_router)
settings_router.include_router(users_router, prefix="/users", tags=["Users Settings"])
settings_router.include_router(roles_router, prefix="/roles", tags=["Roles Settings"])
settings_router.include_router(permission_router, prefix="/permissions", tags=["Permissions Settings"])
