CREATE TABLE IF NOT EXISTS yellow_tripdata (
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

CREATE TABLE IF NOT EXISTS citi_bike_tripdata (
    ride_id TEXT NOT NULL,
    rideable_type TEXT,
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    start_station_name TEXT,
    start_station_id TEXT,
    end_station_name TEXT,
    end_station_id TEXT,
    start_lat DOUBLE PRECISION,
    start_lng DOUBLE PRECISION,
    end_lat DOUBLE PRECISION,
    end_lng DOUBLE PRECISION,
    member_casual TEXT,
    date_hour TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_yellow_tripdata_date_hour
    ON yellow_tripdata (date_hour);

CREATE UNIQUE INDEX IF NOT EXISTS idx_citi_bike_tripdata_ride_id
    ON citi_bike_tripdata (ride_id);

CREATE INDEX IF NOT EXISTS idx_citi_bike_tripdata_date_hour
    ON citi_bike_tripdata (date_hour);
