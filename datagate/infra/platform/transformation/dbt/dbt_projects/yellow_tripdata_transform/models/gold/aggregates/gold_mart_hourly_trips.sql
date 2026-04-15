{{
  config(
    materialized = 'table'
  )
}}

/*
  mart_trip_summary_hourly
  ------------------------
  Gold layer: Hourly demand patterns and revenue metrics.
*/

SELECT
    pickup_hour,
    pickup_day_of_week,
    COUNT(*) AS total_trips,
    ROUND(AVG(total_amount), 2) AS avg_revenue,
    ROUND(AVG(trip_duration_minutes), 2) AS avg_duration
FROM {{ ref('gold_fct_trips') }}
GROUP BY 1, 2
ORDER BY 1, 2
