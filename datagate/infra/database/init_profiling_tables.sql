CREATE TABLE profiling_runs (
    id SERIAL PRIMARY KEY,
    table_name TEXT,
    batch_time TIMESTAMP,
    partition_key TEXT,
    num_records BIGINT,
    raw_json JSONB,
    created_at TIMESTAMP DEFAULT now()
);


CREATE TABLE column_profiles (
    id SERIAL PRIMARY KEY,
    run_id INT REFERENCES profiling_runs(id),

    column_name TEXT,
    data_type TEXT,

    completeness DOUBLE PRECISION,
    approx_distinct BIGINT,

    mean DOUBLE PRECISION,
    min DOUBLE PRECISION,
    max DOUBLE PRECISION,
    stddev DOUBLE PRECISION
);