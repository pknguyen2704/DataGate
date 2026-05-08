DROP TABLE IF EXISTS iceberg.gold.location_hourly_metrics;
DROP TABLE IF EXISTS iceberg.gold.trip_hourly_metrics;
DROP TABLE IF EXISTS iceberg.silver.cleaned_yellow_tripdata;
DROP TABLE IF EXISTS iceberg.bronze.yellow_tripdata;

CREATE SCHEMA IF NOT EXISTS iceberg.bronze
WITH (
    location = 's3://lakehouse/bronze'
);

CREATE SCHEMA IF NOT EXISTS iceberg.silver
WITH (
    location = 's3://lakehouse/silver'
);

CREATE SCHEMA IF NOT EXISTS iceberg.gold
WITH (
    location = 's3://lakehouse/gold'
);
select * from iceberg.bronze.yellow_tripdata

CREATE TABLE iceberg.bronze.yellow_tripdata (
    vendor_id BIGINT,
    tpep_pickup_datetime TIMESTAMP,
    tpep_dropoff_datetime TIMESTAMP,
    passenger_count BIGINT,
    trip_distance DOUBLE,
    ratecode_id BIGINT,
    store_and_fwd_flag VARCHAR,
    pu_location_id BIGINT,
    do_location_id BIGINT,
    payment_type BIGINT,
    fare_amount DOUBLE,
    extra DOUBLE,
    mta_tax DOUBLE,
    tip_amount DOUBLE,
    tolls_amount DOUBLE,
    improvement_surcharge DOUBLE,
    total_amount DOUBLE,
    congestion_surcharge DOUBLE,
    airport_fee DOUBLE,
    cbd_congestion_fee DOUBLE,
    date_hour TIMESTAMP,
    processing_date_hour TIMESTAMP
)
WITH (
    format = 'PARQUET',
    partitioning = ARRAY['processing_date_hour']
);

CREATE TABLE iceberg.silver.cleaned_yellow_tripdata (
    vendor_id BIGINT,
    tpep_pickup_datetime TIMESTAMP,
    tpep_dropoff_datetime TIMESTAMP,
    passenger_count BIGINT,
    trip_distance DOUBLE,
    ratecode_id BIGINT,
    store_and_fwd_flag VARCHAR,
    pu_location_id BIGINT,
    do_location_id BIGINT,
    payment_type BIGINT,
    fare_amount DOUBLE,
    extra DOUBLE,
    mta_tax DOUBLE,
    tip_amount DOUBLE,
    tolls_amount DOUBLE,
    improvement_surcharge DOUBLE,
    total_amount DOUBLE,
    congestion_surcharge DOUBLE,
    airport_fee DOUBLE,
    cbd_congestion_fee DOUBLE,
    date_hour TIMESTAMP,
    processing_date_hour TIMESTAMP
)
WITH (
    format = 'PARQUET',
    partitioning = ARRAY['processing_date_hour']
);

CREATE TABLE IF NOT EXISTS iceberg.gold.trip_hourly_metrics (
    date_hour TIMESTAMP,

    trip_count BIGINT,
    total_passenger_count BIGINT,

    total_trip_distance DOUBLE,
    avg_trip_distance DOUBLE,

    total_fare_amount DOUBLE,
    total_tip_amount DOUBLE,
    total_amount DOUBLE,
    avg_total_amount DOUBLE,

    avg_trip_duration_minutes DOUBLE,
    avg_amount_per_mile DOUBLE,
    avg_tip_rate DOUBLE,

    min_pickup_datetime TIMESTAMP,
    max_pickup_datetime TIMESTAMP,

    processing_date_hour TIMESTAMP
)
WITH (
    format = 'PARQUET',
    partitioning = ARRAY['date_hour']
);

CREATE TABLE IF NOT EXISTS iceberg.gold.location_hourly_metrics (
    date_hour TIMESTAMP,

    pu_location_id BIGINT,
    pickup_borough VARCHAR,
    pickup_zone VARCHAR,
    pickup_service_zone VARCHAR,

    do_location_id BIGINT,
    dropoff_borough VARCHAR,
    dropoff_zone VARCHAR,
    dropoff_service_zone VARCHAR,

    trip_count BIGINT,
    total_passenger_count BIGINT,

    total_trip_distance DOUBLE,
    avg_trip_distance DOUBLE,

    total_fare_amount DOUBLE,
    total_tip_amount DOUBLE,
    total_amount DOUBLE,
    avg_total_amount DOUBLE,

    avg_trip_duration_minutes DOUBLE,

    processing_date_hour TIMESTAMP
)
WITH (
    format = 'PARQUET',
    partitioning = ARRAY['date_hour']
);

SELECT
    committed_at,
    snapshot_id,
    operation,
    element_at(summary, 'added-records') AS added_records,
    element_at(summary, 'added-data-files') AS added_data_files,
    element_at(summary, 'added-files-size') AS added_size_bytes,
FROM iceberg.bronze."yellow_tripdata$snapshots"
ORDER BY committed_at DESC
LIMIT 10;
