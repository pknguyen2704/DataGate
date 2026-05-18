Enum severity_level {
  warning
  critical
}

Enum check_status {
  pass
  fail
  error
}

Enum rule_source {
  system
  manual
}

Enum metric_scope {
  metadata
  profiling
  anomaly
}

Enum check_type {
  metadata_threshold
  profiling_threshold
  rule
  anomaly_auc
}

Table users {
  id uuid [pk]
  username varchar(100) [not null, unique]
  full_name varchar(255)
  email varchar(255) [not null, unique]
  hashed_password varchar(255) [not null]
  role_id uuid [not null]

  created_at timestamptz [not null]
  updated_at timestamptz [not null]

  indexes {
    role_id
  }
}

Table roles {
  id uuid [pk]
  name varchar(100) [not null, unique]
  description text
  permissions jsonb
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
}

Table connections {
  id uuid [pk]
  connection_name varchar(255) [not null, unique]
  description text
  trino_host varchar(255) [not null]
  trino_port int [not null, default: 8080]
  trino_user varchar(255) [not null]
  trino_password text
  iceberg_rest_url varchar(255) [not null]
  iceberg_catalog_name varchar(255) [not null]
  iceberg_warehouse varchar(255) [not null]
  minio_endpoint_url varchar(255) [not null]
  minio_access_key varchar(255) [not null]
  minio_secret_key text [not null]
  is_active boolean [not null, default: true]
  created_by uuid
  last_modified_by uuid
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
}

Table tables {
  id uuid [pk]
  connection_id uuid [not null]
  catalog_name varchar(255) [not null]
  schema_name varchar(255) [not null]
  table_name varchar(255) [not null]
  created_at timestamptz [not null]
  updated_at timestamptz [not null]

  indexes {
    (connection_id, catalog_name, schema_name, table_name) [unique]
  }
}

Table quality_metric_observations {
  id uuid [pk]
  table_id uuid [not null]
  metric_scope metric_scope [not null]
  column_name varchar(255)
  metric_name varchar(255) [not null]
  metric_value float
  extra_data jsonb
  processing_date_hour timestamp [not null]
  created_at timestamptz [not null]
  updated_at timestamptz [not null]

  indexes {
    (table_id, processing_date_hour, metric_scope, column_name, metric_name) [unique]
    (table_id, processing_date_hour)
    (table_id, metric_scope, metric_name)
  }
}

Table quality_thresholds {
  id uuid [pk]
  table_id uuid [not null]
  metric_scope metric_scope [not null]
  column_name varchar(255)
  metric_name varchar(255) [not null]
  min_threshold float
  max_threshold float
  severity_level severity_level [not null, default: "warning"]
  is_active boolean [not null, default: true]
  description text
  created_by uuid
  last_modified_by uuid
  created_at timestamptz [not null]
  updated_at timestamptz [not null]

  indexes {
    (table_id, metric_scope, column_name, metric_name) [unique]
    (table_id, is_active)
  }
}

Table rules {
  id uuid [pk]
  table_id uuid [not null]
  source rule_source [not null, default: "manual"]
  is_active boolean [not null, default: true]
  severity_level severity_level [not null]
  column_name varchar(255)
  constraint_name varchar(512)
  code_for_constraint varchar(512) [not null]
  description text
  current_value varchar(255)
  suggesting_rule varchar(255)
  frequency int [not null, default: 1]
  created_by uuid
  last_modified_by uuid
  created_at timestamptz [not null]
  updated_at timestamptz [not null]

  indexes {
    (table_id, source, column_name, code_for_constraint) [unique]
    (table_id, is_active)
    (table_id, severity_level)
  }
}

Table quality_check_results {
  id uuid [pk]
  table_id uuid [not null]
  check_type check_type [not null]
  threshold_id uuid
  rule_id uuid
  anomaly_result_id uuid
  column_name varchar(255)
  metric_name varchar(255)
  actual_value float
  min_threshold float
  max_threshold float
  status check_status [not null]
  severity_level severity_level
  message text
  is_resolved boolean [not null, default: false]
  resolved_by uuid
  resolved_at timestamptz
  processing_date_hour timestamp [not null]
  created_at timestamptz [not null]
  updated_at timestamptz [not null]

  indexes {
    (table_id, processing_date_hour)
    (table_id, check_type, processing_date_hour)
    (status, severity_level, processing_date_hour)
    is_resolved
  }
}

Table anomaly_configs {
  id uuid [pk]
  table_id uuid [not null, unique]
  batch_time_col varchar(255) [not null]
  feature_config jsonb [not null]
  model_parameters jsonb [not null]
  column_config jsonb [not null]
  description text
  created_by uuid
  last_modified_by uuid
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
}

Table anomaly_results {
  id uuid [pk]
  table_id uuid [not null]
  anomaly_config_id uuid [not null]
  processing_date_hour timestamp [not null]
  auc_score float
  p_value float
  parameter_snapshot jsonb
  feature_config_snapshot jsonb
  shap_top_features jsonb
  created_at timestamptz [not null]
  updated_at timestamptz [not null]

  indexes {
    (table_id, processing_date_hour) [unique]
    (anomaly_config_id, processing_date_hour)
  }
}

Ref: users.role_id > roles.id [delete: restrict]
Ref: connections.created_by > users.id [delete: set null]
Ref: connections.last_modified_by > users.id [delete: set null]
Ref: tables.connection_id > connections.id [delete: cascade]
Ref: quality_metric_observations.table_id > tables.id [delete: cascade]
Ref: quality_thresholds.table_id > tables.id [delete: cascade]
Ref: quality_thresholds.created_by > users.id [delete: set null]
Ref: quality_thresholds.last_modified_by > users.id [delete: set null]
Ref: rules.table_id > tables.id [delete: cascade]
Ref: rules.created_by > users.id [delete: set null]
Ref: rules.last_modified_by > users.id [delete: set null]
Ref: quality_check_results.table_id > tables.id [delete: cascade]
Ref: quality_check_results.threshold_id > quality_thresholds.id [delete: set null]
Ref: quality_check_results.rule_id > rules.id [delete: set null]
Ref: quality_check_results.anomaly_result_id > anomaly_results.id [delete: set null]
Ref: quality_check_results.resolved_by > users.id [delete: set null]
Ref: anomaly_configs.table_id > tables.id [delete: cascade]
Ref: anomaly_configs.created_by > users.id [delete: set null]
Ref: anomaly_configs.last_modified_by > users.id [delete: set null]
Ref: anomaly_results.table_id > tables.id [delete: cascade]
Ref: anomaly_results.anomaly_config_id > anomaly_configs.id [delete: cascade]
