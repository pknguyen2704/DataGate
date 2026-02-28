#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR/../.."
DATA_DIR="$SCRIPT_DIR/../data"

echo "Generating data overview for yellow taxi data..."
"$PROJECT_ROOT/.venv/bin/python3" "$DATA_DIR/data_overview.py" \
  --input "$DATA_DIR/parquet/yellow" \
  --pattern "*.parquet" \
  --out "$DATA_DIR/overview/yellow"

echo "Generating data overview for green taxi data..."
"$PROJECT_ROOT/.venv/bin/python3" "$DATA_DIR/data_overview.py" \
  --input "$DATA_DIR/parquet/green" \
  --pattern "*.parquet" \
  --out "$DATA_DIR/overview/green"
