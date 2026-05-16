CREATE TABLE yellow_tripdata (
    vendor_id SMALLINT,
    tpep_pickup_datetime TIMESTAMP,
    tpep_dropoff_datetime TIMESTAMP,
    passenger_count NUMERIC(10,2),
    trip_distance REAL,
    ratecode_id NUMERIC(10,2),
    store_and_fwd_flag CHAR(1),
    pu_location_id INTEGER,
    do_location_id INTEGER,
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

CREATE TABLE green_tripdata (
    vendor_id SMALLINT,
    lpep_pickup_datetime TIMESTAMP,
    lpep_dropoff_datetime TIMESTAMP,
    store_and_fwd_flag CHAR(1),
    ratecode_id NUMERIC(10,2),
    pu_location_id INTEGER,
    do_location_id INTEGER,
    passenger_count NUMERIC(10,2),
    trip_distance REAL,
    fare_amount NUMERIC(10,2),
    extra NUMERIC(10,2),
    mta_tax NUMERIC(10,2),
    tip_amount NUMERIC(10,2),
    tolls_amount NUMERIC(10,2),
    ehail_fee NUMERIC(10,2),
    improvement_surcharge NUMERIC(10,2),
    total_amount NUMERIC(10,2),
    payment_type SMALLINT,
    trip_type NUMERIC(10,2),
    congestion_surcharge NUMERIC(10,2),
    cbd_congestion_fee NUMERIC(10,2),
    date_hour TIMESTAMP
);
drop table  green_tripdata
select * from yellow_tripdata yt 
select count(*) from yellow_tripdata yt 