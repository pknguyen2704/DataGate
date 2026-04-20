import json
import logging
from pathlib import Path
import requests

from app.core.config import AIRFLOW_URL, AIRFLOW_USER, AIRFLOW_PASS

logger = logging.getLogger(__name__)

DEFAULT_DAG_ID = "data_observability"

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
