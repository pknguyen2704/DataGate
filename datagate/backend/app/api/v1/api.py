from fastapi import APIRouter

from app.api.v1.endpoints.auth import auth_router
from app.api.v1.endpoints.users import user_router
from app.api.v1.endpoints.roles import role_router
from app.api.v1.endpoints.connection import connection_router
from app.api.v1.endpoints.explore import router as explore_router
from app.api.v1.endpoints.rules import rules_router
from app.api.v1.endpoints.tables import table_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(user_router)
api_router.include_router(role_router)
api_router.include_router(connection_router)
api_router.include_router(explore_router)
api_router.include_router(table_router)
api_router.include_router(rules_router)
