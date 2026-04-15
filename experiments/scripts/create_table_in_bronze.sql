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