from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.api import api_router
from app.core.config import config
from app.core.exceptions import AppError


app = FastAPI(
    title=config.app_name,
    version=config.app_version,
    description="DataGate — Data Quality Management Platform.",
    docs_url="/docs",
    redoc_url="/redoc",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppError)
def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message": exc.message,
            "detail": exc.detail,
        },
        headers=exc.headers,
    )


app.include_router(
    api_router,
    prefix=config.api_v1_str,
)


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "version": config.app_version,
    }