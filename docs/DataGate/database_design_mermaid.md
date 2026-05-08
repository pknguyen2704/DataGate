Enum rule_source {
  system
  manual
}

Enum rule_status {
  pending
  active
  inactive
}

Enum rule_severity_level {
  warning
  critical
}

Enum manual_threshold_severity_level {
  warning
  critical
}

Enum metric_result_status {
  pass
  fail
}

Enum lightgbm_verify_status {
  pass
  fail
}

Table users {
  id uuid [pk]
  username varchar(100) [not null]
  full_name varchar(255)
  email varchar(255) [not null]
  hashed_password varchar(255) [not null]
  is_active boolean [not null, default: true]
  created_at timestamp [not null]
  updated_at timestamp [not null]

  indexes {
    username [unique, name: "ix_users__username"]
    email [unique, name: "ix_users__email"]
    is_active [name: "ix_users__is_active"]
  }
}

Table roles {
  id uuid [pk]
  name varchar(100) [not null]
  description text
  is_active boolean [not null, default: true]
  is_system boolean [not null, default: false]
  created_at timestamp [not null]
  updated_at timestamp [not null]

  indexes {
    name [unique, name: "ix_roles__name"]
    is_active [name: "ix_roles__is_active"]
    is_system [name: "ix_roles__is_system"]
  }
}

Table permissions {
  id uuid [pk]
  code varchar(100) [not null]
  name varchar(255) [not null]
  permission_group varchar(100)
  description text
  created_at timestamp [not null]
  updated_at timestamp [not null]

  indexes {
    code [unique, name: "ix_permissions__code"]
    permission_group [name: "ix_permissions__permission_group"]
  }
}

Table user_roles {
  user_id uuid [pk, not null]
  role_id uuid [pk, not null]

  indexes {
    role_id [name: "ix_user_roles__role_id"]
  }
}

Table role_permissions {
  role_id uuid [pk, not null]
  permission_id uuid [pk, not null]

  indexes {
    permission_id [name: "ix_role_permissions__permission_id"]
  }
}

Table connections {
  id uuid [pk]
  connection_name varchar(255) [not null]
  description text

  trino_host varchar(255) [not null]
  trino_port integer [not null, default: 8080]
  trino_user varchar(255) [not null]
  trino_password text

  iceberg_rest_url varchar(255) [not null]
  iceberg_catalog_name varchar(255) [not null]

  minio_endpoint_url varchar(255) [not null]
  minio_access_key varchar(255) [not null]
  minio_secret_key text [not null]

  is_active boolean [not null, default: true]
  created_by uuid
  last_modified_by uuid
  created_at timestamp [not null]
  updated_at timestamp [not null]

  indexes {
    connection_name [unique, name: "ix_connections__connection_name"]
    is_active [name: "ix_connections__is_active"]
    created_by [name: "ix_connections__created_by"]
  }
}

Table tables {
  id uuid [pk]
  connection_id uuid [not null]

  catalog_name varchar(255) [not null]
  schema_name varchar(255) [not null]
  table_name varchar(255) [not null]

  is_active boolean [not null, default: true]
  created_at timestamp [not null]
  updated_at timestamp [not null]

  indexes {
    (connection_id, catalog_name, schema_name, table_name) [unique, name: "ix_tables__connection_catalog_schema_table"]
    connection_id [name: "ix_tables__connection_id"]
    is_active [name: "ix_tables__is_active"]
  }
}

Table rules {
  id uuid [pk]
  table_id uuid [not null]

  source rule_source [not null, default: "manual"]
  status rule_status [not null, default: "pending"]
  severity_level rule_severity_level [not null, default: "warning"]

  column_name varchar(255) [not null]
  constraint_name varchar(512)
  description text
  current_value varchar(255)
  suggesting_rule varchar(255)
  code_for_constraint varchar(512) [not null]
  rule_description text
  frequency integer [not null, default: 1]

  created_by uuid
  last_modified_by uuid
  created_at timestamp [not null]
  updated_at timestamp [not null]

  indexes {
    (table_id, source, column_name, code_for_constraint) [unique, name: "ix_rules__table_source_column_code"]
    (table_id, column_name) [name: "ix_rules__table_column"]
    (table_id, status) [name: "ix_rules__table_status"]
    (table_id, severity_level) [name: "ix_rules__table_severity"]
    (table_id, source, status) [name: "ix_rules__table_source_status"]
  }
}

Table rule_verify {
  id uuid [pk]
  rule_id uuid [not null]
  constraint_status varchar(50) [not null]
  constraint_message text
  processing_date_hour timestamp [not null]
  created_at timestamp [not null]

  indexes {
    (rule_id, processing_date_hour) [unique, name: "ix_rule_verify__rule_hour_unique"]
    (rule_id, processing_date_hour) [name: "ix_rule_verify__rule_hour"]
    (constraint_status, processing_date_hour) [name: "ix_rule_verify__status_hour"]
  }
}

Table batch_table_metadata {
  id uuid [pk]
  table_id uuid [not null]

  batch_added_rows bigint
  batch_added_files integer
  batch_added_files_size_bytes bigint
  table_total_rows bigint
  table_total_files integer
  table_total_size_bytes bigint

  processing_date_hour timestamp [not null]
  created_at timestamp [not null]

  indexes {
    (table_id, processing_date_hour) [unique, name: "ix_batch_table_metadata__table_hour"]
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

  min_length integer
  max_length integer

  distinctness float
  approx_count_distinct bigint

  processing_date_hour timestamp [not null]
  created_at timestamp [not null]

  indexes {
    (table_id, processing_date_hour, column_name) [unique, name: "ix_batch_table_profiling__table_hour_column"]
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

  severity_level manual_threshold_severity_level [not null, default: "warning"]
  is_active boolean [not null, default: true]
  description text

  created_by uuid
  last_modified_by uuid
  created_at timestamp [not null]
  updated_at timestamp [not null]

  indexes {
    (table_id, metric_name) [unique, name: "ix_batch_table_metadata_manual_thresholds__table_metric"]
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
  severity_level manual_threshold_severity_level

  processing_date_hour timestamp [not null]
  created_at timestamp [not null]

  indexes {
    (metadata_manual_threshold_id, batch_table_metadata_id) [unique, name: "ix_batch_table_metadata_metrics_verify__threshold_batch_unique"]
    (metadata_manual_threshold_id, batch_table_metadata_id) [name: "ix_batch_table_metadata_metrics_verify__threshold_batch"]
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

  severity_level manual_threshold_severity_level [not null, default: "warning"]
  is_active boolean [not null, default: true]
  description text

  created_by uuid
  last_modified_by uuid
  created_at timestamp [not null]
  updated_at timestamp [not null]

  indexes {
    (table_id, column_name, metric_name) [unique, name: "ix_batch_table_profiling_manual_thresholds__table_column_metric"]
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
  severity_level manual_threshold_severity_level

  processing_date_hour timestamp [not null]
  created_at timestamp [not null]

  indexes {
    (profiling_manual_threshold_id, batch_table_profiling_id) [unique, name: "ix_batch_table_metadata_metrics_verify__threshold_batch_unique"]
    (profiling_manual_threshold_id, batch_table_profiling_id) [name: "ix_batch_table_metadata_metrics_verify__threshold_batch"]
    (batch_table_profiling_id, status) [name: "ix_batch_table_metadata_metrics_verify__batch_status"]
  }
}

Table lightgbm_parameters {
  id uuid [pk]
  table_id uuid [not null]

  learning_rate float [not null, default: 0.05]
  num_leaves integer [not null, default: 31]
  max_depth integer [not null, default: -1]
  min_data_in_leaf integer [not null, default: 20]
  bagging_fraction float [not null, default: 1.0]
  bagging_freq integer [not null, default: 0]
  feature_fraction float [not null, default: 1.0]
  lambda_l1 float [not null, default: 0.00000001]
  lambda_l2 float [not null, default: 0.00000001]
  min_gain_to_split float [not null, default: 0.0]
  max_bin integer [not null, default: 255]

  num_iterations integer [not null, default: 300]
  use_barrier_execution_mode boolean [not null, default: true]

  created_at timestamp [not null]
  updated_at timestamp [not null]
  created_by uuid
  last_modified_by uuid

  indexes {
    table_id [unique, name: "ix_lgbm_params__table_id"]
  }
}

Table lightgbm_auc {
  id uuid [pk]
  table_id uuid [not null]
  lightgbm_parameter_id uuid [not null]

  processing_date_hour timestamp [not null]

  auc_score float
  p_value float
  num_iterations_used integer
  best_iteration integer
  parameter_snapshot jsonb

  created_at timestamp [not null]

  indexes {
    (table_id, processing_date_hour) [unique, name: "ix_lgbm_results__table_hour_unique"]
    (lightgbm_parameter_id, processing_date_hour) [name: "ix_lgbm_results__param_hour"]
    (table_id, processing_date_hour) [name: "ix_lgbm_results__table_hour"]
  }
}

Table shap_results {
  id uuid [pk]
  lightgbm_result_id uuid [not null]

  feature_name varchar(255) [not null]
  shap_score float [not null]
  shap_rank integer [not null]
  processing_date_hour timestamp [not null]
  created_at timestamp [not null]

  indexes {
    (lightgbm_result_id, feature_name) [unique, name: "ix_shap_results__result_feature"]
    (lightgbm_result_id, shap_rank) [unique, name: "ix_shap_results__result_rank"]
  }
}

Table lightgbm_auc_manual_thresholds {
  id uuid [pk]
  lightgbm_parameter_id uuid [not null]

  auc_threshold float [not null]
  severity_level manual_threshold_severity_level [not null]
  is_active boolean [not null, default: true]
  description text

  created_at timestamp [not null]
  updated_at timestamp [not null]
  created_by uuid
  last_modified_by uuid

  indexes {
    (lightgbm_parameter_id, is_active) [name: "ix_lgbm_thresholds__param_active"]
  }
}

Table lightgbm_auc_verify {
  id uuid [pk]
  lightgbm_result_id uuid [not null]
  manual_threshold_id uuid

  status lightgbm_verify_status [not null]
  auc_score float
  auc_threshold float
  severity_level manual_threshold_severity_level

  processing_date_hour timestamp [not null]
  created_at timestamp [not null]

  indexes {
    lightgbm_result_id [unique, name: "ix_lgbm_verify__result_id"]
    status [name: "ix_lgbm_verify__status"]
  }
}

/* =========================
   Relationships
========================= */

Ref: user_roles.user_id > users.id [delete: cascade]
Ref: user_roles.role_id > roles.id [delete: cascade]

Ref: role_permissions.role_id > roles.id [delete: cascade]
Ref: role_permissions.permission_id > permissions.id [delete: cascade]

Ref: connections.created_by > users.id [delete: set null]
Ref: connections.last_modified_by > users.id [delete: set null]

Ref: tables.connection_id > connections.id [delete: restrict]

Ref: rules.table_id > tables.id [delete: cascade]
Ref: rules.created_by > users.id [delete: set null]
Ref: rules.last_modified_by > users.id [delete: set null]

Ref: rule_verify.rule_id > rules.id [delete: cascade]

Ref: batch_table_metadata.table_id > tables.id [delete: cascade]
Ref: batch_table_profiling.table_id > tables.id [delete: cascade]

Ref: batch_table_metadata_manual_thresholds.table_id > tables.id [delete: cascade]
Ref: batch_table_metadata_manual_thresholds.created_by > users.id [delete: set null]
Ref: batch_table_metadata_manual_thresholds.last_modified_by > users.id [delete: set null]

Ref: batch_table_metadata_metrics_verify.metadata_manual_threshold_id > batch_table_metadata_manual_thresholds.id [delete: cascade]
Ref: batch_table_metadata_metrics_verify.batch_table_metadata_id > batch_table_metadata.id [delete: cascade]

Ref: batch_table_profiling_manual_thresholds.table_id > tables.id [delete: cascade]
Ref: batch_table_profiling_manual_thresholds.created_by > users.id [delete: set null]
Ref: batch_table_profiling_manual_thresholds.last_modified_by > users.id [delete: set null]

Ref: batch_table_metadata_metrics_verify.profiling_manual_threshold_id > batch_table_profiling_manual_thresholds.id [delete: cascade]
Ref: batch_table_metadata_metrics_verify.batch_table_profiling_id > batch_table_profiling.id [delete: cascade]

Ref: lightgbm_parameters.table_id > tables.id [delete: cascade]
Ref: lightgbm_parameters.created_by > users.id [delete: set null]
Ref: lightgbm_parameters.last_modified_by > users.id [delete: set null]

Ref: lightgbm_auc.table_id > tables.id [delete: cascade]
Ref: lightgbm_auc.lightgbm_parameter_id > lightgbm_parameters.id [delete: restrict]

Ref: shap_results.lightgbm_result_id > lightgbm_auc.id [delete: cascade]

Ref: lightgbm_auc_manual_thresholds.lightgbm_parameter_id > lightgbm_parameters.id [delete: cascade]
Ref: lightgbm_auc_manual_thresholds.created_by > users.id [delete: set null]
Ref: lightgbm_auc_manual_thresholds.last_modified_by > users.id [delete: set null]

Ref: lightgbm_auc_verify.lightgbm_result_id > lightgbm_auc.id [delete: cascade]
Ref: lightgbm_auc_verify.manual_threshold_id > lightgbm_auc_manual_thresholds.id [delete: set null]