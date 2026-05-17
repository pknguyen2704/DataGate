import os
from pathlib import Path

DATAGATE_FILES = {
    "anomaly_detection": "batch_anomaly_detection.py",
    "metadata_collection": "batch_metadata_collection_job.py",
    "metadata_metrics_verify": "batch_metadata_metrics_verify.py",
    "profiling_collection": "batch_profiling_collection_job.py",
    "profiling_metrics_verify": "batch_profiling_metrics_verify.py",
    "rule_suggestion": "batch_rule_suggestion.py",
    "rule_verification": "batch_rule_verification.py",
    "data_quality_alert_utils": "data_quality_alert_utils.py",
    "data_quality_gate": "data_quality_gate.py",
}

def datagate_home() -> Path:
    return Path(os.getenv("DATAGATE_HOME", Path(__file__).resolve().parent))


def datagate_job_path(job_name: str) -> str:
    filename = DATAGATE_FILES.get(job_name)
    if filename is None:
        valid_jobs = ", ".join(sorted(DATAGATE_FILES))
        raise ValueError(
            f"Unknown DataGate job: {job_name}. Valid jobs: {valid_jobs}"
        )
    return str(datagate_home() / filename)
