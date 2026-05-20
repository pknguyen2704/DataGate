#!/usr/bin/env bash
set -euo pipefail

SOURCE_FILE="${SOURCE_FILE:-./data/tlc_yellow_tripdata/yellow_tripdata_2025-01.parquet}"
DIRTY_FILE="${DIRTY_FILE:-./data/tlc_yellow_tripdata/yellow_tripdata_2025-01_dirty.parquet}"

uv run python ./scripts/make_dirty_yellow_tripdata.py \
  --file "${SOURCE_FILE}" \
  --output-file "${DIRTY_FILE}" \
  --dirty-date-hours "2025-01-27 12:00:00,2025-01-28 00:00:00" \
  --dirty-ratio 90 \
  --dirty-seed 2025 \
  --overwrite
