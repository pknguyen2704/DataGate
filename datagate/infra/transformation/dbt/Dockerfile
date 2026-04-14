FROM python:3.11-slim

ARG DBT_CORE_VERSION=1.10.1
ARG DBT_TRINO_VERSION=1.10.1

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DBT_PROFILES_DIR=/root/.dbt

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip \
    && pip install "dbt-core==${DBT_CORE_VERSION}" "dbt-trino==${DBT_TRINO_VERSION}" keyring tzdata

WORKDIR /usr/app
CMD ["bash"]