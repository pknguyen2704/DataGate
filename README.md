<div align="center">
  
# DataGate

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0+-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-blue.svg)](https://react.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**DataGate** is a comprehensive Data Quality Management and Observability platform designed to ensure the reliability, accuracy, and health of your data infrastructure. By combining Unsupervised Machine Learning (UML) with traditional rule-based and metrics monitoring, DataGate provides a robust and scalable solution for modern data stacks.

</div>

<hr />

## Table of Contents
- [Key Features](#key-features)
- [Architecture & Tech Stack](#architecture--tech-stack)
- [Repository Structure](#repository-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Running Locally with Docker](#running-locally-with-docker)
  - [Manual Development Setup](#manual-development-setup)
- [Machine Learning Approach](#machine-learning-approach)
- [Contributing](#contributing)
- [Code of Conduct](#code-of-conduct)
- [License](#license)

## Key Features

DataGate relies on four core pillars for data quality monitoring:
- **Data Observability**: Comprehensive metadata tracking (row counts, null rates, schema changes, updates).
- **Unsupervised Machine Learning (UML)**: Automated anomaly detection to find hidden patterns and distribution changes without manual labeling or rule configuration.
- **Rule-Based Testing**: User-defined business rules for deterministic quality checks and critical constraints.
- **Metrics Monitoring**: Tracking and alerting on key statistical metrics over time (e.g., uniqueness, completeness, specific segment health).

### Intelligent Anomaly Detection
- Leverages XGBoost and SHAP for explainable ML models.
- Dynamically adapts to data seasonality and trends to minimize alert fatigue.
- Correlates anomalies across multiple columns and segments to pinpoint root causes.
- Provides granular Anomaly Scores at the cell, row, column, and table levels.

## Architecture & Tech Stack

DataGate is built with a modern, scalable architecture, structured into distinct modules:

- **Backend** (`/datagate/backend`): High-performance REST API built with **Python 3.11**, **FastAPI**, and **SQLAlchemy**. Connects to **PostgreSQL** (via asyncpg/psycopg2) for metadata storage and integrates with **Trino** for federated queries. Uses **Alembic** for migrations and **APScheduler** for task orchestration.
- **Frontend** (`/datagate/frontend`): A responsive, dynamic Single Page Application (SPA) built with **React 19**, **Vite**, **Material UI (MUI)**, and **Redux Toolkit**. Incorporates **ECharts** & **Recharts** for rich data visualizations and observability dashboards.
- **Infrastructure** (`/datagate/infra` & `/datagate/deploy`): Fully containerized using **Docker** and **Docker Compose**, with configurations for orchestration, database provisioning, compute engines, and interactive notebooks. Includes Role-Based Access Control (RBAC) securely built in both backend and frontend layers.

## Repository Structure

```text
DataGate/
├── datagate/
│   ├── backend/         # FastAPI application, database models, schemas, RBAC, API routes
│   ├── frontend/        # React + Vite application, Material UI components, Redux store
│   ├── infra/           # Infrastructure configurations (compute, database, orchestration, notebook)
│   └── deploy/          # Docker and deployment configurations
├── experiments/         # ML experiments, Jupyter notebooks, data quality research docs
└── README.md            # Project overview (you are here)
```

## Getting Started

### Prerequisites
- [Docker](https://www.docker.com/) and Docker Compose
- [Node.js](https://nodejs.org/) (v18+) & [Yarn](https://yarnpkg.com/)
- [Python 3.11+](https://www.python.org/) & `uv` (or pip)

### Running Locally with Docker
The easiest way to run the entire stack is via Docker Compose:
```bash
cd datagate/backend # or datagate/deploy
docker-compose up -d
```

### Manual Development Setup

**1. Backend:**
```bash
cd datagate/backend
# Create and activate virtual environment (or use uv)
uv venv
source .venv/bin/activate
uv pip install -e .
# Or use requirements.txt/pyproject.toml directly
pip install -r requirements.txt # if available

# Run migrations
alembic upgrade head

# Start FastAPI dev server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**2. Frontend:**
```bash
cd datagate/frontend
yarn install
yarn dev
```
The frontend will be available at `http://localhost:5173` and the backend API at `http://localhost:8000`.

## Machine Learning Approach

Unlike traditional monitoring that relies purely on static rules (which miss unknown errors and cause false positives), DataGate employs an automated sampling and classification strategy:
1. **Sampling**: Randomly sample data from "today" vs. historical baselines (yesterday, last week).
2. **Feature Encoding**: Convert complex data types into numerical features.
3. **Classification**: Train an XGBoost classifier to distinguish "today's" data from historical data. If the model can easily tell the difference, a significant structural change (anomaly) has occurred.
4. **Explainability**: SHAP values are extracted to compute anomaly scores and highlight exactly which columns/segments caused the anomaly, providing clear insights into the root cause.

## Contributing

We welcome contributions! Please follow these steps:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature-name`).
3. Commit your changes (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature/your-feature-name`).
5. Open a Pull Request.

For major changes, please open an issue first to discuss what you would like to change.

## Code of Conduct

We are committed to providing a welcoming and inspiring community for all. Please report any unacceptable behavior.

## License

This project is licensed under the [MIT License](LICENSE).
