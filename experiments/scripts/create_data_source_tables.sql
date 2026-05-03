DROP TABLE IF EXISTS green_tripdata;
DROP TABLE IF EXISTS yellow_tripdata;

CREATE TABLE yellow_tripdata (
    vendor_id SMALLINT,
    tpep_pickup_datetime TIMESTAMP,
    tpep_dropoff_datetime TIMESTAMP,
    passenger_count NUMERIC(10,2),
    trip_distance REAL,
    ratecode_id NUMERIC(10,2),
    store_and_fwd_flag CHAR(1),
    pulocationid INTEGER,
    dolocationid INTEGER,
    payment_type SMALLINT,
    fare_amount NUMERIC(10,2),
    extra NUMERIC(10,2),
    mta_tax NUMERIC(10,2),
    tip_amount NUMERIC(10,2),
    tolls_amount NUMERIC(10,2),
    improvement_surcharge NUMERIC(10,2),
    total_amount NUMERIC(10,2),
    congestion_surcharge NUMERIC(10,2),
    airport_fee NUMERIC(10,2),
    cbd_congestion_fee NUMERIC(10,2),
    date_hour TIMESTAMP
);
