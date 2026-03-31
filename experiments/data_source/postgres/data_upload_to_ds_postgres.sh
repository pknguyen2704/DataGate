#!/bin/bash
set -euo pipefail

# =========================================================
# High Performance Upload Script
# Runs seamlessly with relative paths using uv
# =========================================================

DEFAULT_WORKERS=6
DEFAULT_CHUNK_ROWS=200000

# Function to display help
show_help() {
    echo "Usage: ./data_upload_to_postgres.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --data-dir DIR    Directory containing Parquet files"
    echo "  --file FILE       Specific file to upload"
    echo "  --table TABLE     Target table name"
    echo "  --workers N       Number of parallel workers (default: 6)"
    echo "  --chunk-rows N    Chunk size for COPYing (default: 200000)"
    echo "  --date-hour DATE  Filter by date hour (e.g. '2025-01-01 10:00:00')"
    echo "  --help            Show this help message"
    echo ""
    echo "If no arguments are provided, interactive mode will start to guide you through."
}

# Parse basic arguments to intercept --help
for arg in "$@"; do
    if [[ "$arg" == "--help" || "$arg" == "-h" ]]; then
        show_help
        exit 0
    fi
done

USER_DEFINED_WORKERS=false
for arg in "$@"; do
    if [[ "$arg" == "--workers" ]]; then
        USER_DEFINED_WORKERS=true
        break
    fi
done

ARGS=("$@")

if [ "$USER_DEFINED_WORKERS" = false ]; then
    ARGS+=(--workers "$DEFAULT_WORKERS")
fi

if [[ ! " ${ARGS[*]} " =~ " --chunk-rows " ]]; then
    ARGS+=(--chunk-rows "$DEFAULT_CHUNK_ROWS")
fi

echo "======================================="
echo "🚀 Starting High-Performance PostgreSQL Upload"
echo "Workers       : ${DEFAULT_WORKERS} (auto unless overridden)"
echo "Chunk rows    : ${DEFAULT_CHUNK_ROWS}"
echo "======================================="

if [ $# -eq 0 ]; then
    echo "No arguments provided. Starting interactive mode."
    echo ""
    
    read -p "Enter folder or file path to upload (default: parquets/): " input_path
    input_path=${input_path:-parquets/}
    
    read -p "Enter target table name (leave blank for auto-generate): " target_table
    
    read -p "Enter date-hour filter (optional, e.g. '2025-01-01 10:00:00'): " date_hour
    
    INTERACTIVE_ARGS=()
    
    if [ -d "$input_path" ]; then
        INTERACTIVE_ARGS+=(--data-dir "$input_path")
    else
        INTERACTIVE_ARGS+=(--file "$input_path")
    fi
    
    if [ -n "$target_table" ]; then
        INTERACTIVE_ARGS+=(--table "$target_table")
    fi
    
    if [ -n "$date_hour" ]; then
        INTERACTIVE_ARGS+=(--date-hour "$date_hour")
    fi
    
    INTERACTIVE_ARGS+=(--workers "$DEFAULT_WORKERS" --chunk-rows "$DEFAULT_CHUNK_ROWS")
    
    echo ""
    echo "> Commands preview: python data_upload_to_postgres.py ${INTERACTIVE_ARGS[@]}"
    uv run python data_upload_to_postgres.py "${INTERACTIVE_ARGS[@]}"
else
    uv run python data_upload_to_postgres.py "${ARGS[@]}"
fi

echo "✅ Upload process finished."
