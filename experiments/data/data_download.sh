#!/bin/bash
echo "Downloading data..."
uv run python data_download.py --dataset=yellow --year 2025 --months 1-12 --out "parquets/yellow"
uv run python data_download.py --dataset=green --year 2025 --months 1-12 --out "parquets/green"