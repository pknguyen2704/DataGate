# DataGate Data Quality Solution

This folder deploys DataGate as a reusable data quality solution inside `experiments/infra/data_platform`.

## Images

- `datagate-backend`: FastAPI backend and Alembic migrations.
- `datagate-frontend`: static frontend served by Nginx.
- `datagate-jobs`: reusable Airflow/Spark data quality jobs under `/opt/datagate/jobs`.
- `datagate-airflow`: built by the Airflow compose file and includes the same reusable jobs package.

## Deploy

```bash
cp .env.example .env
docker network create datagate-net || true
docker compose -f datagate-compose.yaml --env-file .env build
docker compose -f datagate-compose.yaml --env-file .env --profile migrate run --rm datagate-migrate
docker compose -f datagate-compose.yaml --env-file .env up -d datagate-backend datagate-frontend
```

## Use From ETL/Airflow

Airflow images built from `experiments/infra/data_platform/orchestration/airflow` include `datagate.jobs`.
Use Python jobs through:

```python
from datagate.jobs.data_quality import collect_metadata, evaluate_metadata_metrics
```

Use Spark jobs through:

```python
from datagate.jobs.data_quality import spark_job_path

application = spark_job_path("profiling_collection")
```

Valid Spark job names: `profiling_collection`, `rule_verification`, `rule_suggestion`, `anomaly_detection`.
