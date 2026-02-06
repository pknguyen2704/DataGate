#!/bin/bash

# Activate virtual environment relative to this script
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
python3 "$SCRIPT_DIR/../data/upload_to_postgres.py" "$@"

echo "Upload process finished."
