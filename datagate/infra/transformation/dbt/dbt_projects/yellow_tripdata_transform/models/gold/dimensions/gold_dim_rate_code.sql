/*
  gold_dim_rate_code
  -------------
  Gold layer: Dimensional lookup for rate codes, derived from Silver.
*/

WITH rate_codes_raw AS (
    SELECT DISTINCT ratecodeid
    FROM {{ ref('silver_yellow_tripdata') }}
    WHERE ratecodeid IS NOT NULL
)

SELECT
    ratecodeid AS rate_code_id,
    CASE 
        WHEN ratecodeid = 1 THEN 'Standard rate'
        WHEN ratecodeid = 2 THEN 'JFK'
        WHEN ratecodeid = 3 THEN 'Newark'
        WHEN ratecodeid = 4 THEN 'Nassau or Westchester'
        WHEN ratecodeid = 5 THEN 'Negotiated fare'
        WHEN ratecodeid = 6 THEN 'Group ride'
        WHEN ratecodeid = 99 THEN 'Unknown'
        ELSE 'Other'
    END AS rate_code_name
FROM rate_codes_raw
