CREATE TABLE profile_runs (
    id BIGSERIAL PRIMARY KEY,
    catalog TEXT NOT NULL,
    namespace TEXT NOT NULL,
    table_name TEXT NOT NULL,
    num_records BIGINT,
    profile_json JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_profile_table_time
ON profile_runs(namespace, table_name, created_at DESC);

CREATE INDEX idx_profile_json
ON profile_runs USING GIN (profile_json);

CREATE TABLE constraint_suggestions (
    id BIGSERIAL PRIMARY KEY,
    catalog TEXT NOT NULL,
    namespace TEXT NOT NULL,
    table_name TEXT NOT NULL,
    suggestion_json JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_suggestion_table_time
ON constraint_suggestions(namespace, table_name, created_at DESC);

CREATE INDEX idx_suggestion_json
ON constraint_suggestions USING GIN (suggestion_json);