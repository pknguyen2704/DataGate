#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR/../.."

echo "Starting Data Source..."
cd "$SCRIPT_DIR/../data_source" && docker compose up -d