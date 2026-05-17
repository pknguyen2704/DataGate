uv run python ./scripts/from_parquets_to_data_source.py --file ./data/tlc_yellow_tripdata/yellow_tripdata_2025-01.parquet --table yellow_tripdata --event-col tpep_dropoff_datetime --target-date-hour "2025-01-01 05:00:00"
uv run python ./scripts/from_parquets_to_data_source.py --file ./data/tlc_yellow_tripdata/yellow_tripdata_2025-01.parquet --table yellow_tripdata --event-col tpep_dropoff_datetime

uv run python ./scripts/from_csvs_to_data_source.py --data-dir ./data/citi_bike_tripdata --table public.citi_bike_tripdata --event-col started_at


uv run python ./scripts/make_dirty_data.py \
  --file data/tlc_yellow_tripdata/yellow_tripdata_2025-01.parquet \
  --dirty-date-hours "2025-01-27 12:00:00,2025-01-28 00:00:00" \
  --dirty-ratio 70 \
  --dirty-seed 2025 \
  --overwrite

uv run python ./scripts/make_dirty_citi_bike_tripdata.py \
  --file data/citi_bike_tripdata/202501-citibike-tripdata_1.csv \
  --output-file data/citi_bike_tripdata/202501-citibike-tripdata_1_dirty.csv \
  --dirty-date-hours "2025-01-28 12:00:00,2025-01-29 00:00:00" \
  --dirty-ratio 70 \
  --dirty-seed 2025 \
  --overwrite
