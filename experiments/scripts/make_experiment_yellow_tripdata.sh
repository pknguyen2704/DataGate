#!/usr/bin/env bash
set -euo pipefail

SOURCE_FILE="${SOURCE_FILE:-./data/tlc_yellow_tripdata/yellow_tripdata_2025-01.parquet}"
DIRTY_FILE="${DIRTY_FILE:-./data/tlc_yellow_tripdata/yellow_tripdata_2025-01_experiment.parquet}"

uv run python ./scripts/make_experiment_yellow_tripdata.py \
  --file "${SOURCE_FILE}" \
  --output-file "${DIRTY_FILE}" \
  --event-col "tpep_dropoff_datetime" \
  --dirty-date-hours "2025-01-18 12:00:00, 2025-01-20 12:00:00, 2025-01-22 12:00:00" \
  --dirty-ratio 0.7 \
  --dirty-seed 2025 \
  --overwrite