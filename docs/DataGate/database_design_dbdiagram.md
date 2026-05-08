Enum severity_level {
  warning
  critical
}

Enum metric_result_status {
  pass
  fail
}

Enum lightgbm_result_status {
  pass
  fail
  not_checked
}

Enum rule_source {
  system
  manual
}

Enum rule_status {
  pending
  active
  inactive
}

Table users {
  id uuid [pk]
  username varchar(100) [not null, unique]
  full_name varchar(255)
  email varchar(255) [not null, unique]
  hashed_password varchar(255) [not null]
  is_active boolean [not null, default: true]
  created_at datetime [not null]
  updated_at datetime [not null]
}

Table roles {
  id uuid [pk]
  name varchar(100) [not null, unique]
  description text
  is_active boolean [not null, default: true]
  is_system boolean [not null, default: false]
  created_at datetime [not null]
  updated_at datetime [not null]
}

Table permissions {
  id uuid [pk]
  code varchar(100) [not null, unique]
  name varchar(255) [not null]
  permission_group varchar(100)
  description text
}

Table user_roles {
  user_id uuid [pk, not null]
  role_id uuid [pk, not null]
}

Table role_permissions {
  role_id uuid [pk, not null]
  permission_id uuid [pk, not null]
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
  minio_endpoint_url varchar(255) [not null]
  minio_access_key varchar(255) [not null]
  minio_secret_key text [not null]
  is_active boolean [not null, default: true]
  created_by uuid
  created_at datetime [not null]
  updated_at datetime [not null]
}

Table tables {
  id uuid [pk]
  connection_id uuid [not null]
  catalog_name varchar(255) [not null]
  schema_name varchar(255) [not null]
  table_name varchar(255) [not null]
  is_active boolean [not null, default: true]
  created_at datetime [not null]
  updated_at datetime [not null]

  indexes {
    (connection_id, catalog_name, schema_name, table_name) [unique, name: "uq_tables__connection_catalog_schema_table"]
    connection_id [name: "ix_tables__connection_id"]
    is_active [name: "ix_tables__is_active"]
  }
}

Table batch_table_metadata {
  id uuid [pk]
  table_id uuid [not null]
  batch_added_rows bigint
  batch_added_files int
  table_total_rows bigint
  table_total_files int
  table_total_size_bytes bigint
  processing_date_hour datetime [not null]
  created_at datetime [not null]

  indexes {
    (table_id, processing_date_hour) [unique, name: "uq_batch_table_metadata__table_hour"]
    processing_date_hour [name: "ix_batch_table_metadata__processing_date_hour"]
  }
}

Table batch_table_profiling {
  id uuid [pk]
  table_id uuid [not null]
  column_name varchar(255) [not null]
  data_type varchar(100)
  completeness float
  mean float
  standard_deviation float
  minimum float
  maximum float
  min_length int
  max_length int
  distinctness float
  approx_count_distinct bigint
  processing_date_hour datetime [not null]
  created_at datetime [not null]
  updated_at datetime [not null]

  indexes {
    (table_id, processing_date_hour, column_name) [unique, name: "uq_batch_table_profiling__table_hour_column"]
    (table_id, column_name, processing_date_hour) [name: "ix_batch_table_profiling__table_column_hour"]
    processing_date_hour [name: "ix_batch_table_profiling__processing_date_hour"]
  }
}

Table batch_table_metadata_manual_thresholds {
  id uuid [pk]
  table_id uuid [not null]
  metric_name varchar(255) [not null]
  min_threshold float
  max_threshold float
  severity_level severity_level [not null, default: "warning"]
  is_active boolean [not null, default: true]
  description text
  created_at datetime [not null]
  updated_at datetime [not null]

  indexes {
    (table_id, metric_name) [unique, name: "uq_batch_table_metadata_manual_thresholds__table_metric"]
    (table_id, is_active) [name: "ix_batch_table_metadata_manual_thresholds__table_active"]
    (table_id, metric_name, is_active) [name: "ix_batch_table_metadata_manual_thresholds__lookup"]
  }
}

Table batch_table_metadata_metrics_verify {
  id uuid [pk]
  metadata_manual_threshold_id uuid [not null]
  batch_table_metadata_id uuid [not null]
  actual_value float
  status metric_result_status [not null]
  min_threshold float
  max_threshold float
  severity_level severity_level
  created_at datetime [not null]

  indexes {
    (metadata_manual_threshold_id, batch_table_metadata_id) [unique, name: "uq_batch_table_metadata_metrics_verify__threshold_batch"]
    (batch_table_metadata_id, status) [name: "ix_batch_table_metadata_metrics_verify__batch_status"]
  }
}

Table batch_table_profiling_manual_thresholds {
  id uuid [pk]
  table_id uuid [not null]
  column_name varchar(255) [not null]
  metric_name varchar(255) [not null]
  min_threshold float
  max_threshold float
  severity_level severity_level [not null, default: "warning"]
  is_active boolean [not null, default: true]
  description text
  created_at datetime [not null]
  updated_at datetime [not null]

  indexes {
    (table_id, column_name, metric_name) [unique, name: "uq_batch_table_profiling_manual_thresholds__table_column_metric"]
    (table_id, is_active) [name: "ix_batch_table_profiling_manual_thresholds__table_active"]
    (table_id, column_name, metric_name, is_active) [name: "ix_batch_table_profiling_manual_thresholds__lookup"]
  }
}

Table batch_table_metadata_metrics_verify {
  id uuid [pk]
  profiling_manual_threshold_id uuid [not null]
  batch_table_profiling_id uuid [not null]
  actual_value float
  status metric_result_status [not null]
  min_threshold float
  max_threshold float
  severity_level severity_level
  created_at datetime [not null]

  indexes {
    (profiling_manual_threshold_id, batch_table_profiling_id) [unique, name: "uq_batch_table_metadata_metrics_verify__threshold_batch"]
    (batch_table_profiling_id, status) [name: "ix_batch_table_metadata_metrics_verify__batch_status"]
  }
}

Table lightgbm_parameters {
  id uuid [pk]
  table_id uuid [not null]
  learning_rate float [not null, default: 0.05]
  num_leaves int [not null, default: 31]
  max_depth int [not null, default: -1]
  min_data_in_leaf int [not null, default: 20]
  bagging_fraction float [not null, default: 1.0]
  bagging_freq int [not null, default: 0]
  feature_fraction float [not null, default: 1.0]
  lambda_l1 float [not null, default: 0.00000001]
  lambda_l2 float [not null, default: 0.00000001]
  min_gain_to_split float [not null, default: 0.0]
  max_bin int [not null, default: 255]
  num_iterations int [not null, default: 300]
  early_stopping_round int [not null, default: 30]
  use_barrier_execution_mode boolean [not null, default: true]
  is_active boolean [not null, default: true]
  description text
  created_at datetime [not null]
  updated_at datetime [not null]
}

Table lightgbm_auc_manual_thresholds {
  id uuid [pk]
  lightgbm_parameter_id uuid [not null]
  auc_min_threshold float
  auc_max_threshold float
  severity_level severity_level [not null, default: "warning"]
  is_active boolean [not null, default: true]
  description text
  created_at datetime [not null]
  updated_at datetime [not null]
}

Table lightgbm_auc {
  id uuid [pk]
  lightgbm_parameter_id uuid [not null]
  manual_threshold_id uuid
  processing_date_hour datetime [not null]
  auc_score float
  status lightgbm_result_status [not null, default: "not_checked"]
  auc_min_threshold float
  auc_max_threshold float
  severity_level severity_level
  message text
  created_at datetime [not null]
  updated_at datetime [not null]
}

Table shap_results {
  id uuid [pk]
  lightgbm_result_id uuid [not null]
  feature_name varchar(255) [not null]
  shap_score float [not null]
  shap_rank int
  created_at datetime [not null]
}

Table rules {
  id uuid [pk]
  table_id uuid [not null]
  source rule_source [not null, default: "manual"]
  status rule_status [not null, default: "pending"]
  severity_level severity_level [not null, default: "warning"]
  column_name varchar(255) [not null]
  constraint_name varchar(512)
  description text
  frequency int [not null, default: 1]
  current_value varchar(255)
  suggesting_rule varchar(255)
  code_for_constraint varchar(512) [not null]
  rule_description text
  created_by uuid
  last_modified_by uuid
  created_at datetime [not null]
  updated_at datetime [not null]
}

Table rule_verify {
  id uuid [pk]
  rule_id uuid [not null]
  constraint_status varchar(50) [not null]
  constraint_message text
  processing_date_hour datetime [not null]
  created_at datetime [not null]
  updated_at datetime [not null]
}

Ref: user_roles.user_id > users.id
Ref: user_roles.role_id > roles.id
Ref: role_permissions.role_id > roles.id
Ref: role_permissions.permission_id > permissions.id
Ref: connections.created_by > users.id
Ref: tables.connection_id > connections.id
Ref: batch_table_metadata.table_id > tables.id
Ref: batch_table_profiling.table_id > tables.id
Ref: batch_table_metadata_manual_thresholds.table_id > tables.id
Ref: batch_table_metadata_metrics_verify.metadata_manual_threshold_id > batch_table_metadata_manual_thresholds.id
Ref: batch_table_metadata_metrics_verify.batch_table_metadata_id > batch_table_metadata.id
Ref: batch_table_profiling_manual_thresholds.table_id > tables.id
Ref: batch_table_metadata_metrics_verify.profiling_manual_threshold_id > batch_table_profiling_manual_thresholds.id
Ref: batch_table_metadata_metrics_verify.batch_table_profiling_id > batch_table_profiling.id
Ref: lightgbm_parameters.table_id > tables.id
Ref: lightgbm_auc_manual_thresholds.lightgbm_parameter_id > lightgbm_parameters.id
Ref: lightgbm_auc.lightgbm_parameter_id > lightgbm_parameters.id
Ref: lightgbm_auc.manual_threshold_id > lightgbm_auc_manual_thresholds.id
Ref: shap_results.lightgbm_result_id > lightgbm_auc.id
Ref: rules.table_id > tables.id
Ref: rules.created_by > users.id
Ref: rules.last_modified_by > users.id
Ref: rule_verify.rule_id > rules.id