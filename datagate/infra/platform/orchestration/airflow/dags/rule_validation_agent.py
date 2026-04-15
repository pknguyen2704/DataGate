from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta


default_args = {
    "owner": "datagate",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


dag = DAG(
    "rule_validation_agent",
    default_args=default_args,
    description="Generate dbt schema from applied rules, run dbt test, and sync results",
    schedule_interval=None,
    catchup=False,
    tags=["datagate", "rules", "dbt", "quality"],
)


validate_rules_task = BashOperator(
    task_id="validate_applied_rules",
    bash_command="""
        docker exec \
            -e DATAGATE_TARGET_TABLE={{ dag_run.conf.get('table', '') }} \
            -e DATAGATE_BACKEND_URL=http://host.docker.internal:8000 \
            dbt bash -lc '
              cd /usr/app/yellow_tripdata_transform && \
              python generate_rules.py && \
              dbt test --select {{ dag_run.conf.get("model", "silver_yellow_tripdata") }}; TEST_EXIT=$?; \
              python sync_test_results.py; \
              exit $TEST_EXIT
            '
    """,
    dag=dag,
)


validate_rules_task
