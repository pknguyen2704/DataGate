from app.api.v1.endpoints import profiling, services, rules
from fastapi import APIRouter
import subprocess
import os

api_router = APIRouter()
api_router.include_router(profiling.router, prefix="/profiling", tags=["profiling"])
api_router.include_router(services.router, prefix="/services", tags=["services"])
api_router.include_router(rules.router, prefix="/rules", tags=["rules"])
