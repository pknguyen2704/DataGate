{{
  config(
    materialized = 'table'
  )
}}

/*
  gold_fct_trips
  ---------
  Gold layer: Core fact table containing all cleaned trips.
*/

WITH raw_trips AS (
    SELECT * FROM {{ ref('silver_yellow_tripdata') }}
),
payment_types AS (
    SELECT * FROM {{ ref('gold_dim_payment_type') }}
),
rate_codes AS (
    SELECT * FROM {{ ref('gold_dim_rate_code') }}
),
enriched AS (
    SELECT
        -- ── Identifiers ──────────────────────────────────────────────────────────
        vendorid,

        -- ── Trip timeline ─────────────────────────────────────────────────────
        tpep_pickup_datetime                                        AS pickup_datetime,
        tpep_dropoff_datetime                                       AS dropoff_datetime,

        -- ── Passenger & distance ──────────────────────────────────────────────
        passenger_count,
        trip_distance                                               AS trip_distance_miles,

        -- ── Rate & location ──────────────────────────────────────────────────
        ratecodeid                                                  AS rate_code_id,
        store_and_fwd_flag,
        pulocationid                                               AS pickup_location_id,
        dolocationid                                               AS dropoff_location_id,

        -- ── Payment ──────────────────────────────────────────────────────────
        payment_type                                                AS payment_type_id,

        -- ── Financial fields ────────
        fare_amount,
        extra                                                       AS extra_amount,
        mta_tax,
        tip_amount,
        tolls_amount,
        improvement_surcharge,
        total_amount,
        congestion_surcharge,
        airport_fee,
        cbd_congestion_fee,

        -- ── Partition column ──────────────────────────────────────────────
        date_hour                                                  AS pickup_date_hour,

        -- ── Derived metrics ───────────────────────────────────────────────────
        ROUND(
            CAST(date_diff('second', tpep_pickup_datetime, tpep_dropoff_datetime) AS DOUBLE) / 60.0,
            2
        )                                                                   AS trip_duration_minutes,

        CASE
            WHEN date_diff('second', tpep_pickup_datetime, tpep_dropoff_datetime) > 0
            THEN ROUND(
                    trip_distance
                    / (CAST(date_diff('second', tpep_pickup_datetime, tpep_dropoff_datetime) AS DOUBLE) / 3600.0),
                    2
                 )
            ELSE 0.0
        END                                                                 AS trip_speed_mph,

        -- Revenue without tip
        ROUND(
            fare_amount + extra + mta_tax + tolls_amount
            + improvement_surcharge + congestion_surcharge + airport_fee + cbd_congestion_fee,
            2
        )                                                                   AS revenue_excl_tip,

        -- Airport trip flag (JFK=132, LGA=138, EWR=1)
        CASE
            WHEN pulocationid  IN (1, 132, 138)
              OR dolocationid IN (1, 132, 138)
            THEN TRUE
            ELSE FALSE
        END                                                                 AS is_airport_trip,

        -- Date parts
        CAST(date_trunc('day',  tpep_pickup_datetime) AS DATE)                   AS pickup_date,
        CAST(hour(tpep_pickup_datetime) AS INTEGER)                              AS pickup_hour,
        day_of_week(tpep_pickup_datetime)                                        AS pickup_day_of_week   -- 1=Mon … 7=Sun

    FROM raw_trips
)

SELECT
    -- Key columns
    md5(to_utf8(cast(e.vendorid as varchar) || cast(e.pickup_datetime as varchar) || cast(e.pickup_location_id as varchar) || cast(e.dropoff_datetime as varchar) || cast(e.total_amount as varchar))) AS trip_id,
    e.vendorid,
    
    -- Date & Time
    e.pickup_datetime,
    e.dropoff_datetime,
    e.pickup_date,
    e.pickup_hour,
    e.pickup_day_of_week,
    e.pickup_date_hour,
    
    -- Metrics
    e.passenger_count,
    e.trip_distance_miles,
    e.fare_amount,
    e.extra_amount,
    e.mta_tax,
    e.tip_amount,
    e.tolls_amount,
    e.improvement_surcharge,
    e.total_amount,
    e.congestion_surcharge,
    e.airport_fee,
    e.cbd_congestion_fee,
    e.trip_duration_minutes,
    e.trip_speed_mph,
    e.revenue_excl_tip,
    e.is_airport_trip,

    -- Dimensional Links
    e.rate_code_id,
    rd.rate_code_name,
    e.payment_type_id,
    pd.payment_type_name,
    
    -- Locations
    e.pickup_location_id,
    e.dropoff_location_id

FROM enriched e
LEFT JOIN payment_types pd ON e.payment_type_id = pd.payment_type_id
LEFT JOIN rate_codes rd ON e.rate_code_id = rd.rate_code_id
