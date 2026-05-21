#!/usr/bin/env bash
set -euo pipefail

SOURCE_FILE="${1:-./data/tlc_yellow_tripdata/yellow_tripdata_2025-01_experiment.parquet}"

uv run python ./scripts/upload_data_to_data_source.py \
  --file "${SOURCE_FILE}" \
  --table yellow_tripdata \
  --event-col tpep_dropoff_datetime
