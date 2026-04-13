{{
  config(
    materialized = 'table',
    on_table_exists = 'drop'
  )
}}

/*
  silver_yellow_tripdata
  --------------------
  Silver layer: Clean and standardize raw NYC Yellow Taxi trip records.
  Keeps the same schema as Bronze but applies Medallion cleaning rules:
  - Null/zero passenger_count → default to 1
  - Negative financial fields → ABS()
  - Invalid payment_type → remap to 5 (Unknown)
  - Filter rows: valid timeline and positive distance
*/

WITH source AS (
    SELECT * FROM {{ source('bronze', 'yellow_tripdata') }}
),

cleaned AS (
    SELECT
        vendorid,
        tpep_pickup_datetime,
        tpep_dropoff_datetime,
        COALESCE(NULLIF(CAST(passenger_count AS INTEGER), 0), 1)   AS passenger_count,
        COALESCE(trip_distance, 0.0)                               AS trip_distance,
        COALESCE(ratecodeid, CAST(1 AS BIGINT))                    AS ratecodeid,
        store_and_fwd_flag,
        pulocationid,
        dolocationid,
        CASE
            WHEN payment_type IN (1, 2, 3, 4, 5, 6) THEN payment_type
            ELSE 5   -- 5 = Unknown
        END AS payment_type,
        ABS(COALESCE(fare_amount,            0.0))                 AS fare_amount,
        ABS(COALESCE(extra,                  0.0))                 AS extra,
        ABS(COALESCE(mta_tax,                0.0))                 AS mta_tax,
        ABS(COALESCE(tip_amount,             0.0))                 AS tip_amount,
        ABS(COALESCE(tolls_amount,           0.0))                 AS tolls_amount,
        ABS(COALESCE(improvement_surcharge,  0.0))                 AS improvement_surcharge,
        ABS(COALESCE(total_amount,           0.0))                 AS total_amount,
        ABS(COALESCE(congestion_surcharge,   0.0))                 AS congestion_surcharge,
        ABS(COALESCE(airport_fee,            0.0))                 AS airport_fee,
        COALESCE(cbd_congestion_fee,         0.0)                  AS cbd_congestion_fee,
        date_hour
    FROM source
    WHERE tpep_pickup_datetime  IS NOT NULL
      AND tpep_dropoff_datetime IS NOT NULL
      AND tpep_dropoff_datetime  > tpep_pickup_datetime
      AND trip_distance          > 0
)

SELECT * FROM cleaned
