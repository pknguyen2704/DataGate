import json
import logging
from pathlib import Path
import requests

from app.core.config import settings
from app.models.observability_model import DGObservabilityConfig

logger = logging.getLogger(__name__)

AIRFLOW_URL = settings.AIRFLOW_URL
AIRFLOW_USER = settings.AIRFLOW_USER
AIRFLOW_PASS = settings.AIRFLOW_PASS
DEFAULT_DAG_ID = "dq_metadata_collector"
METADATA_PROFILE_PREFIX = "dq_metadata_profile_job_"
AIRFLOW_DAGS_DIR = Path(__file__).resolve().parents[3] / "infra" / "platform" / "orchestration" / "airflow" / "dags"
GENERATED_CONFIGS_DIR = AIRFLOW_DAGS_DIR / "generated_configs"
DAG_FACTORY_FILE = AIRFLOW_DAGS_DIR / "dq_metadata_profile_factory.py"


def build_metadata_profile_conf(job: DGObservabilityConfig, trigger_type: str = "manual") -> dict:
    return {
        "job_id": job.id,
        "job_type": job.job_type or "metadata_profile",
        "trigger_type": trigger_type,
        "catalog": job.catalog,
        "schema": job.schema_name,
        "table": job.table_name,
    }


def build_metadata_profile_dag_id(job_id: int) -> str:
    return f"{METADATA_PROFILE_PREFIX}{job_id}"


def sync_metadata_profile_dag(job: DGObservabilityConfig):
    GENERATED_CONFIGS_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "job_id": job.id,
        "dag_id": job.dag_id or build_metadata_profile_dag_id(job.id),
        "job_type": job.job_type or "metadata_profile",
        "catalog": job.catalog,
        "schema_name": job.schema_name,
        "table_name": job.table_name,
        "schedule_type": job.schedule_type or "daily",
        "interval_minutes": job.interval_minutes,
        "hour": job.hour,
        "minute": job.minute,
        "is_active": bool(job.is_active),
    }

    config_path = GENERATED_CONFIGS_DIR / f"{payload['dag_id']}.json"
    config_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    touch_airflow_dag_factory()
    return config_path


def cleanup_metadata_profile_dag(dag_id: str | None):
    if not dag_id:
        return

    config_path = GENERATED_CONFIGS_DIR / f"{dag_id}.json"
    if config_path.exists():
        config_path.unlink()

    touch_airflow_dag_factory()


def touch_airflow_dag_factory():
    if DAG_FACTORY_FILE.exists():
        DAG_FACTORY_FILE.touch()


def trigger_airflow_dag(dag_id: str = DEFAULT_DAG_ID, conf: dict | None = None):
    url = f"{AIRFLOW_URL}/api/v1/dags/{dag_id}/dagRuns"
    payload = {"conf": conf or {}}

    try:
        response = requests.post(
            url,
            json=payload,
            auth=(AIRFLOW_USER, AIRFLOW_PASS),
            timeout=10,
        )
        response.raise_for_status()
        logger.info("Triggered Airflow DAG %s", dag_id)
        return response.json()
    except Exception as exc:
        logger.error("Failed to trigger Airflow DAG %s: %s", dag_id, exc)
        return {"error": str(exc)}
