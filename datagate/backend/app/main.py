from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os

from app.api.v1.api import api_router
from app.core.config import config
from app.core.exceptions import AppError


app = FastAPI(
    title=config.app_name,
    version=config.app_version,
    description="DataGate - Data Quality Management Platform",
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


# Health check endpoint
@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "version": config.app_version,
    }


# Serve Frontend SPA
STATIC_DIR = "/app/static"
if os.path.exists(STATIC_DIR):
    @app.middleware("http")
    async def spa_fallback_middleware(request: Request, call_next):
        response = await call_next(request)
        if response.status_code == 404 and not request.url.path.startswith("/api/"):
            index_path = os.path.join(STATIC_DIR, "index.html")
            if os.path.exists(index_path):
                return FileResponse(index_path)
        return response

    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
