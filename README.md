# DataGate

<div align="center">

![DataGate](https://img.shields.io/badge/DataGate-Modern_Data_Platform-blue?style=for-the-badge&logo=postgresql)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)

**Modular, Containerized, and Scalable Data Platform**

</div>

## 📖 Overview

**DataGate** is a modern data platform engineered to demonstrate an end-to-end data lifecycle. It integrates best-in-class open-source technologies to handle data ingestion, storage, processing, and visualization.

The platform relies on a Lakehouse architecture using **Apache Iceberg** and **MinIO**, orchestrated by **Airflow**, processed by **Spark**, and queried via **Trino**.

## 🏗 Architecture

The platform is organized into loosely coupled modules:

| Component | Technology | Description |
|-----------|------------|-------------|
| **Data Source** | PostgreSQL | Simulates operational databases (OLTP). |
| **Storage** | MinIO (S3) | Object storage for the Data Lake. |
| **Table Format** | Apache Iceberg | High-performance table format for the Lakehouse. |
| **Catalog** | Iceberg REST | Manages table metadata. |
| **Compute** | Apache Spark | Batch processing and heavy transformations. |
| **Query Engine** | Trino | Fast distributed SQL query engine. |
| **Orchestration** | Apache Airflow | Workflow automation and scheduling. |
| **Transformation** | dbt | SQL-based data transformation in the warehouse. |
| **Monitoring** | Prometheus & Grafana | Observability and metrics. |

## 🚀 Getting Started

### Prerequisites

- **Docker** and **Docker Compose**
- **Python 3.10+**
- **Git**

### Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/pknguyen2704/DataGate.git
    cd DataGate
    ```

2.  **Setup Environment**:
    ```bash
    ./setup.sh
    ```

3.  **Run the Platform**:
    Navigate to `experiments/data_platform` and start the components:
    ```bash
    cd experiments/data_platform
    
    # Start Storage & Catalog
    docker compose -f storage/minio/docker-compose.yaml up -d
    docker compose -f catalog/REST_catalog/docker-compose.yaml up -d
    
    # Start Compute & Query
    docker compose -f compute_engine/spark/docker-compose.yaml up -d
    docker compose -f query_engine/trino/docker-compose.yaml up -d
    
    # Start Orchestration
    docker compose -f orchestration/airflow/docker-compose.yaml up -d
    ```

## 📂 Project Structure

```text
DataGate/
├── apps/               # Application applications
├── docs/               # Documentation
├── experiments/        # Core platform experiments and configs
│   ├── data/           # Raw data samples
│   ├── data_platform/  # Dockerized platform components
│   ├── data_source/    # Source database simulations
│   └── scripts/        # Utility scripts (download, upload, setup)
├── integrations/       # External integration tests
├── setup.sh            # Global setup script
└── requirements.txt    # Python dependencies
```

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) and [Code of Conduct](CODE_OF_CONDUCT.md) for details on how to participate.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
