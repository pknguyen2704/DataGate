from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.api.v1.api import api_router
from app.db.session import engine
from app.db.base_class import Base
from contextlib import asynccontextmanager
import app.models.profiling
import app.models.service
import app.models.rule
import app.models.auth
import app.models.observability

from app.services.observability_scheduler import check_and_trigger_jobs
from apscheduler.schedulers.background import BackgroundScheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure tables are created
    Base.metadata.create_all(bind=engine)
    
    # Start scheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_and_trigger_jobs, 'cron', minute='*')
    scheduler.start()
    yield
    # Shutdown scheduler
    scheduler.shutdown()

app = FastAPI(title="DataGate API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

# Legacy compatibility for URLs without v1
app.include_router(api_router, prefix="/api")

@app.get("/health")
def health_check():
    return {"status": "healthy"}
