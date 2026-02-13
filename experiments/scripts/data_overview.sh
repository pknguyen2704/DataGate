#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR/../.."
DATA_DIR="$SCRIPT_DIR/../data"

echo "Generating data overview..."
"$PROJECT_ROOT/.venv/bin/python3" "$DATA_DIR/data_overview.py" \
  --input "$DATA_DIR/parquet" \
  --pattern "*.parquet" \
  --out "$DATA_DIR/overview"
