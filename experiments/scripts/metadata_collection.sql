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

latest_metadata AS (
    SELECT
        latest_snapshot_id,
        latest_schema_id,
        latest_sequence_number,
        timestamp AS metadata_recorded_at
    FROM iceberg.bronze."yellow_tripdata$metadata_log_entries"
    ORDER BY timestamp DESC
    LIMIT 1
)

SELECT
    'iceberg' AS catalog_name,
    'bronze' AS schema_name,
    'yellow_tripdata' AS table_name,

    s.snapshot_id,
    s.parent_id AS parent_snapshot_id,
    s.operation,
    s.committed_at AS last_updated_time,

    COALESCE(
        TRY_CAST(element_at(s.summary, 'added-records') AS BIGINT),
        0
    ) AS batch_added_rows,

    COALESCE(
        TRY_CAST(element_at(s.summary, 'added-data-files') AS BIGINT),
        TRY_CAST(element_at(s.summary, 'added-files') AS BIGINT),
        0
    ) AS batch_added_files,

    COALESCE(
        TRY_CAST(element_at(s.summary, 'deleted-records') AS BIGINT),
        0
    ) AS deleted_rows,

    COALESCE(
        TRY_CAST(element_at(s.summary, 'deleted-data-files') AS BIGINT),
        TRY_CAST(element_at(s.summary, 'deleted-files') AS BIGINT),
        0
    ) AS deleted_files,

    TRY_CAST(element_at(s.summary, 'total-records') AS BIGINT) AS table_total_rows,
    TRY_CAST(element_at(s.summary, 'total-data-files') AS BIGINT) AS table_total_files,
    TRY_CAST(element_at(s.summary, 'total-files-size') AS BIGINT) AS table_total_size_bytes,

    TRY_CAST(element_at(s.summary, 'changed-partition-count') AS BIGINT) AS changed_partition_count,

    m.latest_schema_id AS schema_id,
    m.latest_sequence_number,
    m.metadata_recorded_at,

    current_timestamp AS collected_at

FROM latest_snapshot s
LEFT JOIN latest_metadata m
    ON m.latest_snapshot_id = s.snapshot_id;


SELECT
    'iceberg' AS catalog_name,
    table_schema AS schema_name,
    table_name,
    column_name,
    data_type AS column_type,
    ordinal_position,
    is_nullable,
    current_timestamp AS collected_at
FROM iceberg.information_schema.columns
WHERE table_schema = 'bronze'
  AND table_name = 'yellow_tripdata'
ORDER BY ordinal_position;