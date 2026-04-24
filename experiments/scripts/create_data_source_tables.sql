CREATE TABLE yellow_tripdata (
    VendorID INTEGER,
    tpep_pickup_datetime TIMESTAMP,
    tpep_dropoff_datetime TIMESTAMP,
    passenger_count DOUBLE PRECISION,
    trip_distance DOUBLE PRECISION,
    RatecodeID DOUBLE PRECISION,
    store_and_fwd_flag TEXT,
    PULocationID INTEGER,
    DOLocationID INTEGER,
    payment_type INTEGER,
    fare_amount DOUBLE PRECISION,
    extra DOUBLE PRECISION,
    mta_tax DOUBLE PRECISION,
    tip_amount DOUBLE PRECISION,
    tolls_amount DOUBLE PRECISION,
    improvement_surcharge DOUBLE PRECISION,
    total_amount DOUBLE PRECISION,
    congestion_surcharge DOUBLE PRECISION,
    Airport_fee DOUBLE PRECISION,
    cbd_congestion_fee DOUBLE PRECISION,
    date_hour TIMESTAMP
);

CREATE TABLE IF NOT EXISTS green_tripdata (
    VendorID INTEGER,
    lpep_pickup_datetime TIMESTAMP,
    lpep_dropoff_datetime TIMESTAMP,
    store_and_fwd_flag TEXT,
    RatecodeID DOUBLE PRECISION,
    PULocationID DOUBLE PRECISION,
    DOLocationID DOUBLE PRECISION,
    passenger_count DOUBLE PRECISION,
    trip_distance DOUBLE PRECISION,
    fare_amount DOUBLE PRECISION,
    extra DOUBLE PRECISION,
    mta_tax DOUBLE PRECISION,
    tip_amount DOUBLE PRECISION,
    tolls_amount DOUBLE PRECISION,
    ehail_fee DOUBLE PRECISION,
    improvement_surcharge DOUBLE PRECISION,
    total_amount DOUBLE PRECISION,
    payment_type DOUBLE PRECISION,
    trip_type DOUBLE PRECISION,
    congestion_surcharge DOUBLE PRECISION,
    cbd_congestion_fee DOUBLE PRECISION,
    date_hour TIMESTAMP
);
drop table public.yellow_tripdata

select * from yellow_tripdata
select count(distinct date_hour) from yellow_tripdata


SELECT DISTINCT date_hour::date AS date
FROM yellow_tripdata
WHERE date_hour >= TIMESTAMP '2025-01-01'
  AND date_hour <  TIMESTAMP '2025-02-01'
ORDER BY date;