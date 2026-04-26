select count(*) from iceberg.bronze.yellow_tripdata 
drop table iceberg.bronze.yellow_tripdata 

CREATE TABLE iceberg.bronze.yellow_tripdata (
    vendorid BIGINT,
    tpep_pickup_datetime TIMESTAMP,
    tpep_dropoff_datetime TIMESTAMP,
    passenger_count BIGINT,
    trip_distance DOUBLE,
    ratecodeid BIGINT,
    store_and_fwd_flag VARCHAR,
    pulocationid BIGINT,
    dolocationid BIGINT,
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
    date_hour TIMESTAMP
)
WITH (
    format = 'PARQUET',
    partitioning = ARRAY['date_hour']
);

describe iceberg.bronze."yellow_tripdata$history"
select * from iceberg.bronze."yellow_tripdata$history"
DESCRIBE iceberg.bronze."yellow_tripdata$snapshots";
select * from iceberg.bronze."yellow_tripdata$snapshots";

CREATE TABLE iceberg.silver.cleaned_yellow_tripdata (
    vendorid BIGINT,
    tpep_pickup_datetime TIMESTAMP,
    tpep_dropoff_datetime TIMESTAMP,
    passenger_count BIGINT,
    trip_distance DOUBLE,
    ratecodeid BIGINT,
    store_and_fwd_flag VARCHAR,
    pulocationid BIGINT,
    dolocationid BIGINT,
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
    date_hour TIMESTAMP
)
WITH (
    format = 'PARQUET',
    partitioning = ARRAY['date_hour']
);
drop table iceberg.silver.yellow_tripdata 


CREATE TABLE iceberg.gold.yellow_tripdata_enriched (
    vendorid BIGINT,
    tpep_pickup_datetime TIMESTAMP,
    tpep_dropoff_datetime TIMESTAMP,
    passenger_count BIGINT,
    trip_distance DOUBLE,
    ratecodeid BIGINT,
    store_and_fwd_flag VARCHAR,
    pulocationid BIGINT,
    dolocationid BIGINT,
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

    trip_duration_minutes DOUBLE,
    amount_per_mile DOUBLE,
    tip_rate DOUBLE
)
WITH (
    format = 'PARQUET',
    partitioning = ARRAY['date_hour']
);

CREATE TABLE iceberg.gold.trip_hourly_metrics (
    date_hour TIMESTAMP,

    trip_count BIGINT,
    total_passenger_count BIGINT,

    total_trip_distance DOUBLE,
    avg_trip_distance DOUBLE,

    total_fare_amount DOUBLE,
    total_tip_amount DOUBLE,
    total_total_amount DOUBLE,
    avg_total_amount DOUBLE,

    avg_trip_duration_minutes DOUBLE,

    min_pickup_datetime TIMESTAMP,
    max_pickup_datetime TIMESTAMP,
    min_dropoff_datetime TIMESTAMP,
    max_dropoff_datetime TIMESTAMP
)
WITH (
    format = 'PARQUET',
    partitioning = ARRAY['date_hour']
);

CREATE TABLE iceberg.gold.location_hourly_metrics (
    date_hour TIMESTAMP,
    pulocationid BIGINT,
    dolocationid BIGINT,

    trip_count BIGINT,
    total_passenger_count BIGINT,

    total_trip_distance DOUBLE,
    avg_trip_distance DOUBLE,

    total_fare_amount DOUBLE,
    total_tip_amount DOUBLE,
    total_total_amount DOUBLE,
    avg_total_amount DOUBLE
)
WITH (
    format = 'PARQUET',
    partitioning = ARRAY['date_hour']
);

CREATE TABLE iceberg.gold.payment_hourly_metrics (
    date_hour TIMESTAMP,
    payment_type BIGINT,

    trip_count BIGINT,
    total_trip_distance DOUBLE,

    total_fare_amount DOUBLE,
    total_tip_amount DOUBLE,
    total_total_amount DOUBLE,
    avg_total_amount DOUBLE,

    avg_tip_rate DOUBLE
)
WITH (
    format = 'PARQUET',
    partitioning = ARRAY['date_hour']
);

CREATE TABLE iceberg.gold.vendor_hourly_metrics (
    date_hour TIMESTAMP,
    vendorid BIGINT,

    trip_count BIGINT,
    total_passenger_count BIGINT,

    total_trip_distance DOUBLE,
    avg_trip_distance DOUBLE,

    total_fare_amount DOUBLE,
    total_tip_amount DOUBLE,
    total_total_amount DOUBLE,
    avg_total_amount DOUBLE
)

