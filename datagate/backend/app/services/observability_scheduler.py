import logging
import requests
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.observability import DQJobConfig
from app.core.config import settings
import os

logger = logging.getLogger(__name__)

AIRFLOW_URL = settings.AIRFLOW_URL
AIRFLOW_USER = settings.AIRFLOW_USER
AIRFLOW_PASS = settings.AIRFLOW_PASS
DAG_ID = "dq_metadata_collector"

def trigger_airflow_dag(dag_id: str, conf: dict):
    """Calls Airflow 2.x REST API v1 to trigger a specific DAG"""
    url = f"{AIRFLOW_URL}/api/v1/dags/{dag_id}/dagRuns"
    
    payload = {
        "conf": conf
    }
    
    try:
        response = requests.post(
            url,
            json=payload,
            auth=(AIRFLOW_USER, AIRFLOW_PASS),
            timeout=10
        )
        if response.status_code in [200, 201]:
            logger.info(f"🚀 Triggered Airflow 2.x DAG: {dag_id}")
            return response.json()
        else:
            logger.error(f"❌ Failed to trigger Airflow 2.x {dag_id}: {response.text}")
            return {"error": response.json()}
    except Exception as e:
        logger.error(f"❌ Error calling Airflow 2.x API for {dag_id}: {e}")
        return {"error": str(e)}

def trigger_metadata_collector(config: DQJobConfig):
    """Backward compatible wrapper for scheduled metadata jobs"""
    return trigger_airflow_dag(
        DAG_ID, 
        conf={
            "catalog": config.catalog,
            "schema": config.schema_name,
            "table": config.table_name,
            "job_id": config.id
        }
    )

def check_and_trigger_jobs():
    """Checked dq_job_config for jobs matching current hour and minute"""
    now = datetime.now()
    hour = now.hour
    minute = now.minute
    
    db = SessionLocal()
    try:
        active_jobs = db.query(DQJobConfig).filter(
            DQJobConfig.is_active == True,
            DQJobConfig.hour == hour,
            DQJobConfig.minute == minute
        ).all()
        
        for job in active_jobs:
            logger.info(f"⏰ Found scheduled job for {job.table_name} at {hour}:{minute}")
            trigger_metadata_collector(job)
            
    except Exception as e:
        logger.error(f"❌ Scheduler error: {e}")
    finally:
        db.close()
