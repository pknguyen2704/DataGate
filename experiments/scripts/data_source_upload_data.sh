#!/bin/bash
set -euo pipefail

# =========================================================
# Run example:
# ./data_source_upload_data.sh \
#   --file ../data/parquet/yellow/yellow_tripdata_2025-01.parquet \
#   --table yellow_tripdata
#   --date-hour "2025-01-01 10:00:00"
#
# Or:
# ./data_source_upload_data.sh
# =========================================================


SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR/../.."

PY_SCRIPT="$SCRIPT_DIR/../data_source/postgres/upload_to_postgres.py"
DATA_DIR="$PROJECT_ROOT/experiments/data/parquet"

# -----------------------------------------
# Default performance tuning (4C/8T CPU)
# -----------------------------------------

DEFAULT_WORKERS=6          # tốt cho 4C/8T (I/O bound)
DEFAULT_CHUNK_ROWS=200000  # COPY chunk size


# -----------------------------------------
# Detect if user already provided workers
# -----------------------------------------

USER_DEFINED_WORKERS=false
for arg in "$@"; do
    if [[ "$arg" == "--workers" ]]; then
        USER_DEFINED_WORKERS=true
        break
    fi
done

# -----------------------------------------
# Auto-build argument list
# -----------------------------------------

ARGS=("$@")

if [ "$USER_DEFINED_WORKERS" = false ]; then
    ARGS+=(--workers "$DEFAULT_WORKERS")
fi

# Add default chunk size if not provided
if [[ ! " ${ARGS[*]} " =~ " --chunk-rows " ]]; then
    ARGS+=(--chunk-rows "$DEFAULT_CHUNK_ROWS")
fi

# -----------------------------------------
# Execute
# -----------------------------------------

echo "======================================="
echo "🚀 Starting PostgreSQL Upload"
echo "Python script : $PY_SCRIPT"
echo "Workers       : ${DEFAULT_WORKERS} (auto unless overridden)"
echo "Chunk rows    : ${DEFAULT_CHUNK_ROWS}"
echo "======================================="

if [ $# -eq 0 ]; then
    echo "No arguments provided. Using default data directory: $DATA_DIR"
    python3 "$PY_SCRIPT" \
        --data-dir "$DATA_DIR" \
        "${ARGS[@]}"
else
    python3 "$PY_SCRIPT" "${ARGS[@]}"
fi

echo "✅ Upload process finished."