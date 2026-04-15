/*
  gold_dim_payment_type
  ----------------
  Gold layer: Dimensional lookup for payment types, derived from Silver.
*/

WITH payment_types_raw AS (
    SELECT DISTINCT payment_type
    FROM {{ ref('silver_yellow_tripdata') }}
    WHERE payment_type IS NOT NULL
)

SELECT
    payment_type AS payment_type_id,
    CASE 
        WHEN payment_type = 1 THEN 'Credit card'
        WHEN payment_type = 2 THEN 'Cash'
        WHEN payment_type = 3 THEN 'No charge'
        WHEN payment_type = 4 THEN 'Dispute'
        WHEN payment_type = 5 THEN 'Unknown'
        WHEN payment_type = 6 THEN 'Voided trip'
        ELSE 'Other'
    END AS payment_type_name
FROM payment_types_raw
