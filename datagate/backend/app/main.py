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
import app.models.quality

OBSERVABILITY_DDL = [
    "ALTER TABLE dq_job_config ADD COLUMN IF NOT EXISTS schedule_type TEXT DEFAULT 'daily'",
    "ALTER TABLE dq_job_config ADD COLUMN IF NOT EXISTS interval_minutes INTEGER",
    "ALTER TABLE dq_job_config ADD COLUMN IF NOT EXISTS dag_id TEXT DEFAULT 'dq_metadata_collector'",
    "ALTER TABLE dq_job_config ADD COLUMN IF NOT EXISTS last_run_at TIMESTAMP",
    "ALTER TABLE dq_job_config ALTER COLUMN hour DROP NOT NULL",
    "ALTER TABLE dq_job_config ALTER COLUMN minute DROP NOT NULL",
    "ALTER TABLE ml_anomaly_runs ADD COLUMN IF NOT EXISTS raw_json JSONB",
    "ALTER TABLE active_rules ADD COLUMN IF NOT EXISTS category TEXT DEFAULT 'validity'",
    "ALTER TABLE active_rules ADD COLUMN IF NOT EXISTS priority TEXT DEFAULT 'medium'",
    "ALTER TABLE active_rules ADD COLUMN IF NOT EXISTS source TEXT DEFAULT 'manual'",
    "ALTER TABLE active_rules ADD COLUMN IF NOT EXISTS description TEXT",
    "ALTER TABLE active_rules ADD COLUMN IF NOT EXISTS confidence_score DOUBLE PRECISION",
    "ALTER TABLE active_rules ADD COLUMN IF NOT EXISTS is_applied BOOLEAN DEFAULT false",
    "ALTER TABLE active_rules ADD COLUMN IF NOT EXISTS last_result_status TEXT",
    "ALTER TABLE active_rules ADD COLUMN IF NOT EXISTS last_failure_message TEXT",
    "ALTER TABLE active_rules ADD COLUMN IF NOT EXISTS last_validated_at TIMESTAMP",
    "ALTER TABLE quality_check_results ADD COLUMN IF NOT EXISTS rule_id INTEGER REFERENCES active_rules(id)",
    """
    CREATE TABLE IF NOT EXISTS dq_job_run_history (
        id BIGSERIAL PRIMARY KEY,
        job_id INTEGER NOT NULL REFERENCES dq_job_config(id),
        dag_id TEXT,
        dag_run_id TEXT,
        trigger_type TEXT DEFAULT 'scheduled',
        status TEXT DEFAULT 'queued',
        scheduled_for TIMESTAMP NULL,
        started_at TIMESTAMP NULL,
        finished_at TIMESTAMP NULL,
        error_message TEXT NULL,
        created_at TIMESTAMP DEFAULT now()
    )
    """,
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure tables are created
    Base.metadata.create_all(bind=engine)

    with engine.begin() as connection:
        for statement in OBSERVABILITY_DDL:
            connection.execute(text(statement))

    yield

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
