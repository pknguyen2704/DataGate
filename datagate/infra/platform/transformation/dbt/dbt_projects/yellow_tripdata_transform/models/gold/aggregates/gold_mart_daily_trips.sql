{{
  config(
    materialized = 'table'
  )
}}

/*
  mart_trip_summary_daily
  -----------------------
  Gold layer: Daily aggregated KPIs for business monitoring.
*/

SELECT
    pickup_date,
    COUNT(*) AS total_trips,
    SUM(passenger_count) AS total_passengers,
    ROUND(SUM(trip_distance_miles), 2) AS total_distance_miles,
    ROUND(SUM(total_amount), 2) AS total_revenue,
    ROUND(AVG(total_amount), 2) AS avg_fare_per_trip,
    ROUND(AVG(trip_duration_minutes), 2) AS avg_duration_minutes,
    ROUND(AVG(trip_speed_mph), 2) AS avg_speed_mph,
    COUNT(CASE WHEN is_airport_trip THEN 1 END) AS airport_trips_count
FROM {{ ref('gold_fct_trips') }}
GROUP BY 1
ORDER BY 1 DESC
