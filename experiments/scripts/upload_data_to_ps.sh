uv run python ./scripts/from_parquets_to_data_source.py --file ./data/parquets/yellow/yellow_tripdata_2024-01.parquet --table yellow_tripdata --event-col tpep_dropoff_datetime --target-date-hour "2025-01-01 00:00:00"
uv run python ./scripts/from_parquets_to_data_source.py --file ./data/parquets/yellow/yellow_tripdata_2025-01.parquet --table yellow_tripdata --event-col tpep_dropoff_datetime 

# uv run python ./data_source/postgres/upload_data_to_postgres.py --file ./data/parquets/yellow/yellow_tripdata_2025-02.parquet --table yellow_tripdata --if-exists replace
uv run python ./data_source/postgres/upload_data_to_postgres.py --file ./data/parquets/green/green_tripdata_2025-01.parquet --table green_tripdata --if-exists replace
# uv run python ./data_source/postgres/upload_data_to_postgres.py --file ./data/parquets/green/green_tripdata_2025-02.parquet --table green_tripdata --if-exists replace

