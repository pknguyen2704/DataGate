from app.api.v1.endpoints import (
    connections_router, 
    auth_router, 
    users_router, 
    observability_router, 
    explore_router
)
from fastapi import APIRouter

api_router = APIRouter(redirect_slashes=False)
api_router.include_router(auth_router.router, prefix="/auth", tags=["auth"])
api_router.include_router(users_router.router, prefix="/users", tags=["users"])
api_router.include_router(connections_router.router, prefix="/connections", tags=["connections"])
api_router.include_router(explore_router.router, prefix="/explore", tags=["explore"])
api_router.include_router(observability_router.router, prefix="/observability", tags=["observability"])
