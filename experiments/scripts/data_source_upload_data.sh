#!/bin/bash

# Activate virtual environment relative to this script
# Script run
# ./data_source_upload_data.sh --file ../data/parquet/yellow_tripdata_2025-01.parquet --table yellow_tripdata

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR/../.."

# Ensure venv exists
if [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
    source "$PROJECT_ROOT/.venv/bin/activate"
else
    echo "Virtual environment not found at $PROJECT_ROOT/.venv"
    exit 1
fi

# Run the upload script
# Assuming data is in experiments/data/parquet (based on previous context)
DATA_DIR="$PROJECT_ROOT/experiments/data/parquet"

echo "Starting data upload..."
if [ $# -eq 0 ]; then
    echo "No arguments provided. Using default data directory: $DATA_DIR"
    python3 "$SCRIPT_DIR/../data_source/upload_to_postgres.py" --data-dir "$DATA_DIR"
else
    python3 "$SCRIPT_DIR/../data_source/upload_to_postgres.py" "$@"
fi

echo "Upload process finished."
