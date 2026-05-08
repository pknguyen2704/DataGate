from fastapi import APIRouter, Depends, Query, status

quality_router = APIRouter(prefix="/quality", tags=["Quality"])

# Include metadata verify, profiling verify, rule verify, anomaly detection verify result