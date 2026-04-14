from app.api.v1.endpoints import profiling, services, rules, auth, users, quality, ml_quality, observability
from fastapi import APIRouter
import subprocess
import os

api_router = APIRouter()
api_router.include_router(profiling.router, prefix="/profiling", tags=["profiling"])
api_router.include_router(services.router, prefix="/services", tags=["services"])
api_router.include_router(rules.router, prefix="/rules", tags=["rules"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(quality.router, prefix="/quality", tags=["quality"])
api_router.include_router(ml_quality.router, prefix="/ml", tags=["ml"])
api_router.include_router(observability.router, prefix="/observability", tags=["observability"])
