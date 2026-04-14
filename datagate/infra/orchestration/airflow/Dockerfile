FROM apache/airflow:2.11.2

USER airflow
RUN pip install --no-cache-dir \
    "astronomer-cosmos[docker]" \
    apache-airflow-providers-docker \
    apache-airflow-providers-trino \
    apache-airflow-providers-postgres \
    psycopg2-binary
