import json
import os
import sys
from datetime import datetime

import requests


RUN_RESULTS_PATH = os.getenv("DBT_RUN_RESULTS_PATH", "./target/run_results.json")
TARGET_TABLE = os.getenv("DATAGATE_TARGET_TABLE")
BACKEND_URL = os.getenv("DATAGATE_BACKEND_URL", "http://host.docker.internal:8000")


def normalize_result(entry):
    unique_id = entry.get("unique_id", "")
    test_metadata = entry.get("test_metadata") or {}
    kwargs = test_metadata.get("kwargs") or {}
    column_name = kwargs.get("column_name") or kwargs.get("column") or unique_id.split(".")[-1]
    rule_type = test_metadata.get("name") or unique_id.split(".")[-2] if "." in unique_id else "dbt_test"
    status = entry.get("status", "error")
    failures = entry.get("failures")
    message = entry.get("message") or f"dbt test status={status}, failures={failures}"
    return {
        "rule_id": None,
        "column_name": column_name,
        "rule_type": rule_type,
        "constraint_status": "Success" if status == "pass" else "Failure",
        "constraint_message": message,
        "severity": "Error" if status in {"fail", "error"} else "Info",
    }


def main():
    if not os.path.exists(RUN_RESULTS_PATH):
        raise FileNotFoundError(f"run_results.json not found at {RUN_RESULTS_PATH}")
    if not TARGET_TABLE:
        raise ValueError("DATAGATE_TARGET_TABLE is required")

    with open(RUN_RESULTS_PATH, "r", encoding="utf-8") as handle:
        run_results = json.load(handle)

    entries = run_results.get("results", [])
    normalized = [normalize_result(entry) for entry in entries]
    failed_checks = sum(1 for item in normalized if item["constraint_status"] != "Success")

    payload = {
        "table_name": TARGET_TABLE,
        "batch_time": datetime.utcnow().isoformat(),
        "partition_key": datetime.utcnow().date().isoformat(),
        "total_checks": len(normalized),
        "failed_checks": failed_checks,
        "status": "FAILURE" if failed_checks else "SUCCESS",
        "results": normalized,
    }

    response = requests.post(f"{BACKEND_URL}/api/v1/quality/runs/internal", json=payload, timeout=30)
    response.raise_for_status()
    print(f"Synchronized {len(normalized)} dbt test results for {TARGET_TABLE}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Failed to sync dbt results: {exc}")
        sys.exit(1)
