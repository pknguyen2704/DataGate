-- 0. Drop tables if you want a clean start (Optional)
-- DROP TABLE IF EXISTS column_histograms;
-- DROP TABLE IF EXISTS column_profiles;
-- DROP TABLE IF EXISTS profile_runs;

-- 1. Table for Run Metadata (History)
CREATE TABLE IF NOT EXISTS profile_runs (
    id SERIAL PRIMARY KEY,
    catalog TEXT NOT NULL,
    namespace TEXT NOT NULL,
    table_name TEXT NOT NULL,
    num_records BIGINT,
    raw_json JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Table for detailed column metrics
CREATE TABLE IF NOT EXISTS column_profiles (
    id SERIAL PRIMARY KEY,
    run_id INTEGER REFERENCES profile_runs(id) ON DELETE CASCADE,
    column_name TEXT NOT NULL,
    data_type TEXT,
    completeness DOUBLE PRECISION,
    approx_distinct_values BIGINT,
    mean DOUBLE PRECISION,
    maximum DOUBLE PRECISION,
    minimum DOUBLE PRECISION,
    sum DOUBLE PRECISION,
    std_dev DOUBLE PRECISION
);

-- 3. Table for Histograms (Distribution)
CREATE TABLE IF NOT EXISTS column_histograms (
    id SERIAL PRIMARY KEY,
    column_profile_id INTEGER REFERENCES column_profiles(id) ON DELETE CASCADE,
    bin_value TEXT,
    absolute_count BIGINT,
    ratio DOUBLE PRECISION
);

-- Create some indexes for faster querying
CREATE INDEX IF NOT EXISTS idx_profile_runs_table ON profile_runs(table_name);
CREATE INDEX IF NOT EXISTS idx_column_profiles_run ON column_profiles(run_id);
CREATE INDEX IF NOT EXISTS idx_column_histograms_profile ON column_histograms(column_profile_id);
