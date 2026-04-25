select count(*) from iceberg.bronze.yellow_tripdata 
drop table iceberg.bronze.yellow_tripdata 

CREATE TABLE iceberg.bronze.yellow_tripdata (
    vendorid BIGINT,
    tpep_pickup_datetime TIMESTAMP,
    tpep_dropoff_datetime TIMESTAMP,
    passenger_count BIGINT,
    trip_distance DOUBLE,
    ratecodeid BIGINT,
    store_and_fwd_flag VARCHAR,
    pulocationid BIGINT,
    dolocationid BIGINT,
    payment_type BIGINT,
    fare_amount DOUBLE,
    extra DOUBLE,
    mta_tax DOUBLE,
    tip_amount DOUBLE,
    tolls_amount DOUBLE,
    improvement_surcharge DOUBLE,
    total_amount DOUBLE,
    congestion_surcharge DOUBLE,
    airport_fee DOUBLE,
    cbd_congestion_fee DOUBLE,
    date_hour TIMESTAMP
)
WITH (
    format = 'PARQUET',
    partitioning = ARRAY['date_hour']
);

describe iceberg.bronze."yellow_tripdata$history"
select * from iceberg.bronze."yellow_tripdata$history"
DESCRIBE iceberg.bronze."yellow_tripdata$snapshots";
select * from iceberg.bronze."yellow_tripdata$snapshots";

WITH latest_snapshot AS (
    SELECT
        committed_at,
        snapshot_id,
        parent_id,
        operation,
        summary
    FROM iceberg.bronze."yellow_tripdata$snapshots"
    ORDER BY committed_at DESC
    LIMIT 1
),

manifest_stats AS (
    SELECT
        m.added_snapshot_id AS snapshot_id,

        SUM(m.added_data_files_count) AS batch_added_files,
        SUM(m.added_rows_count) AS batch_added_rows,

        SUM(m.existing_data_files_count) AS existing_files,
        SUM(m.existing_rows_count) AS existing_rows,

        SUM(m.deleted_data_files_count) AS deleted_files,
        SUM(m.deleted_rows_count) AS deleted_rows
    FROM iceberg.bronze."yellow_tripdata$manifests" m
    JOIN latest_snapshot s
        ON m.added_snapshot_id = s.snapshot_id
    GROUP BY m.added_snapshot_id
),

current_table_stats AS (
    SELECT
        COUNT(*) AS current_file_count,
        SUM(record_count) AS current_total_rows,
        SUM(file_size_in_bytes) AS current_total_size_bytes
    FROM iceberg.bronze."yellow_tripdata$files"
),

column_metadata AS (
    SELECT
        ARRAY_AGG(
            CAST(
                ROW(
                    column_name,
                    data_type,
                    ordinal_position,
                    is_nullable
                )
                AS ROW(
                    column_name VARCHAR,
                    column_type VARCHAR,
                    ordinal_position INTEGER,
                    is_nullable VARCHAR
                )
            )
            ORDER BY ordinal_position
        ) AS columns
    FROM iceberg.information_schema.columns
    WHERE table_schema = 'bronze'
      AND table_name = 'yellow_tripdata'
)

SELECT
    -- Table identity
    'iceberg' AS catalog_name,
    'bronze' AS schema_name,
    'yellow_tripdata' AS table_name,

    -- Snapshot metadata
    s.snapshot_id,
    s.parent_id AS parent_snapshot_id,
    s.operation,
    s.committed_at AS last_updated_time,

    -- Batch-level changes
    COALESCE(
        m.batch_added_rows,
        TRY_CAST(element_at(s.summary, 'added-records') AS BIGINT)
    ) AS batch_added_rows,

    COALESCE(
        m.batch_added_files,
        TRY_CAST(element_at(s.summary, 'added-data-files') AS BIGINT),
        TRY_CAST(element_at(s.summary, 'added-files') AS BIGINT)
    ) AS batch_added_files,

    m.existing_rows,
    m.existing_files,
    m.deleted_rows,
    m.deleted_files,

    -- Table-level stats after commit
    TRY_CAST(element_at(s.summary, 'total-records') AS BIGINT) AS table_total_rows_after_commit,
    TRY_CAST(element_at(s.summary, 'total-data-files') AS BIGINT) AS table_total_files_after_commit,
    TRY_CAST(element_at(s.summary, 'total-files-size') AS BIGINT) AS table_total_size_bytes_after_commit,

    -- Current file-level table stats
    f.current_file_count,
    f.current_total_rows,
    f.current_total_size_bytes,

    -- Schema / partition change metadata
    TRY_CAST(element_at(s.summary, 'changed-partition-count') AS BIGINT) AS changed_partition_count,

    -- Column metadata
    c.columns AS column_metadata,

    -- Collection time
    current_timestamp AS collected_at

FROM latest_snapshot s
LEFT JOIN manifest_stats m
    ON s.snapshot_id = m.snapshot_id
CROSS JOIN current_table_stats f
CROSS JOIN column_metadata c;