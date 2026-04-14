#!/bin/bash

# Configuration: DataGate Backend API URL
# If running inside Docker on Mac: http://host.docker.internal:8000
# If running on same network: http://datagate_backend:8000
BACKEND_API_URL="http://host.docker.internal:8000/api/v1/rules/generate"

echo "=========================================================="
echo "🚀 DATA GATE: Syncing Rules & Running DBT Transformation"
echo "=========================================================="

# 1. Trigger schema generation locally (Internal to dbt container)
echo "Step 1: Generating dbt schema from DataGate Rules (Internal)..."

# Ensure dbt project variables are used for DB connection if needed
# export DATAGATE_DB_HOST="datagate_database" 

python3 generate_rules.py

if [ $? -eq 0 ]; then
    echo "✅ Schema updated locally."
else
    echo "❌ Error generating schema. Aborting."
    exit 1
fi

# 2. Run & Test transformation (Integrated)
echo "Step 2: Executing dbt build (Run + Test)..."
dbt build

if [ $? -eq 0 ]; then
    echo "----------------------------------------------------------"
    echo "✨ Transformation complete!"
else
    echo "----------------------------------------------------------"
    echo "⚠️ dbt run failed. Check logs above."
    exit 1
fi
