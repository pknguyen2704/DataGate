uv run python3 ./data_source/postgres/upload_data_to_postgres.py --file ./data/parquets/yellow/yellow_tripdata_2025-01.parquet --table yellow_tripdata --if-exists replace
uv run python3 ./data_source/postgres/upload_data_to_postgres.py --file ./data/parquets/green/green_tripdata_2025-01.parquet --table green_tripdata --if-exists replace
