#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR/.."
DATA_DIR="$SCRIPT_DIR/../data"

echo "Downloading data..."
"$PROJECT_ROOT/.venv/bin/python3" "$DATA_DIR/download_data_tlc.py" --year 2025 --months 1-12 --out "$DATA_DIR/parquet/yellow"
"$PROJECT_ROOT/.venv/bin/python3" "$DATA_DIR/download_data_tlc.py" --dataset=green --year 2025 --months 1-12 --out "$DATA_DIR/parquet/green"