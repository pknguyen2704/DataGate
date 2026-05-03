class PermissionCode:
    ADMIN = "admin"

    USER_VIEW = "user:view"
    USER_CREATE = "user:create"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"

    ROLE_VIEW = "role:view"
    ROLE_CREATE = "role:create"
    ROLE_UPDATE = "role:update"
    ROLE_DELETE = "role:delete"
    ROLE_ASSIGN_PERMISSION = "role:assign_permission"

    CONNECTION_VIEW = "connection:view"
    CONNECTION_CREATE = "connection:create"
    CONNECTION_UPDATE = "connection:update"
    CONNECTION_DELETE = "connection:delete"
    CONNECTION_TEST = "connection:test"

    TABLE_VIEW = "table:view"
    TABLE_CREATE = "table:create"
    TABLE_UPDATE = "table:update"
    TABLE_DELETE = "table:delete"
    TABLE_GRANT_ACCESS = "table:grant_access"
    TABLE_REVOKE_ACCESS = "table:revoke_access"

    TABLE_MANAGE_THRESHOLDS = "table:manage_thresholds"
    TABLE_MANAGE_RULES = "table:manage_rules"

    METADATA_VIEW = "metadata:view"
    METADATA_COLLECT = "metadata:collect"
    OBSERVABILITY_VIEW = "observability:view"

    RULE_VIEW = "rule:view"
    RULE_CREATE = "rule:create"
    RULE_UPDATE = "rule:update"
    RULE_DELETE = "rule:delete"
    RULE_ENABLE_DISABLE = "rule:enable_disable"
    RULE_SUGGEST = "rule:suggest"

    QUALITY_VIEW = "quality:view"
    QUALITY_RUN = "quality:run"

    THRESHOLD_VIEW = "threshold:view"
    THRESHOLD_CREATE = "threshold:create"
    THRESHOLD_UPDATE = "threshold:update"
    THRESHOLD_DELETE = "threshold:delete"

    ANOMALY_VIEW = "anomaly:view"
    ANOMALY_RUN = "anomaly:run"

    ALERT_VIEW = "alert:view"
    ALERT_UPDATE_STATUS = "alert:update_status"
    ALERT_ACKNOWLEDGE = "alert:acknowledge"

    JOB_VIEW = "job:view"
    JOB_TRIGGER = "job:trigger"

    DASHBOARD_VIEW = "dashboard:view"


ALL_PERMISSIONS = [
    {"code": PermissionCode.ADMIN, "name": "Super Admin", "group": "System"},

    {"code": PermissionCode.USER_VIEW, "name": "View Users", "group": "User Management"},
    {"code": PermissionCode.USER_CREATE, "name": "Create User", "group": "User Management"},
    {"code": PermissionCode.USER_UPDATE, "name": "Update User", "group": "User Management"},
    {"code": PermissionCode.USER_DELETE, "name": "Delete User", "group": "User Management"},

    {"code": PermissionCode.ROLE_VIEW, "name": "View Roles", "group": "Role Management"},
    {"code": PermissionCode.ROLE_CREATE, "name": "Create Role", "group": "Role Management"},
    {"code": PermissionCode.ROLE_UPDATE, "name": "Update Role", "group": "Role Management"},
    {"code": PermissionCode.ROLE_DELETE, "name": "Delete Role", "group": "Role Management"},
    {"code": PermissionCode.ROLE_ASSIGN_PERMISSION, "name": "Assign Permission to Role", "group": "Role Management"},

    {"code": PermissionCode.CONNECTION_VIEW, "name": "View Connections", "group": "Connection Management"},
    {"code": PermissionCode.CONNECTION_CREATE, "name": "Create Connection", "group": "Connection Management"},
    {"code": PermissionCode.CONNECTION_UPDATE, "name": "Update Connection", "group": "Connection Management"},
    {"code": PermissionCode.CONNECTION_DELETE, "name": "Delete Connection", "group": "Connection Management"},
    {"code": PermissionCode.CONNECTION_TEST, "name": "Test Connection", "group": "Connection Management"},

    {"code": PermissionCode.TABLE_VIEW, "name": "View Tables", "group": "Table Management"},
    {"code": PermissionCode.TABLE_CREATE, "name": "Register Table", "group": "Table Management"},
    {"code": PermissionCode.TABLE_UPDATE, "name": "Update Table", "group": "Table Management"},
    {"code": PermissionCode.TABLE_DELETE, "name": "Delete Table", "group": "Table Management"},
    {"code": PermissionCode.TABLE_GRANT_ACCESS, "name": "Grant Table Access", "group": "Table Management"},
    {"code": PermissionCode.TABLE_REVOKE_ACCESS, "name": "Revoke Table Access", "group": "Table Management"},

    {"code": PermissionCode.TABLE_MANAGE_THRESHOLDS, "name": "Manage Table Thresholds", "group": "Table Owner"},
    {"code": PermissionCode.TABLE_MANAGE_RULES, "name": "Manage Table Rules", "group": "Table Owner"},

    {"code": PermissionCode.METADATA_VIEW, "name": "View Metadata", "group": "Metadata"},
    {"code": PermissionCode.METADATA_COLLECT, "name": "Collect Metadata", "group": "Metadata"},
    {"code": PermissionCode.OBSERVABILITY_VIEW, "name": "View Observability", "group": "Metadata"},

    {"code": PermissionCode.RULE_VIEW, "name": "View Rules", "group": "Rule Management"},
    {"code": PermissionCode.RULE_CREATE, "name": "Create Rule", "group": "Rule Management"},
    {"code": PermissionCode.RULE_UPDATE, "name": "Update Rule", "group": "Rule Management"},
    {"code": PermissionCode.RULE_DELETE, "name": "Delete Rule", "group": "Rule Management"},
    {"code": PermissionCode.RULE_ENABLE_DISABLE, "name": "Enable/Disable Rule", "group": "Rule Management"},
    {"code": PermissionCode.RULE_SUGGEST, "name": "Suggest Rules", "group": "Rule Management"},

    {"code": PermissionCode.QUALITY_VIEW, "name": "View Quality Results", "group": "Data Quality"},
    {"code": PermissionCode.QUALITY_RUN, "name": "Run Quality Validation", "group": "Data Quality"},

    {"code": PermissionCode.THRESHOLD_VIEW, "name": "View Thresholds", "group": "Threshold Management"},
    {"code": PermissionCode.THRESHOLD_CREATE, "name": "Create Threshold", "group": "Threshold Management"},
    {"code": PermissionCode.THRESHOLD_UPDATE, "name": "Update Threshold", "group": "Threshold Management"},
    {"code": PermissionCode.THRESHOLD_DELETE, "name": "Delete Threshold", "group": "Threshold Management"},

    {"code": PermissionCode.ANOMALY_VIEW, "name": "View Anomaly Results", "group": "Anomaly Detection"},
    {"code": PermissionCode.ANOMALY_RUN, "name": "Run Anomaly Detection", "group": "Anomaly Detection"},

    {"code": PermissionCode.ALERT_VIEW, "name": "View Alerts", "group": "Alert Management"},
    {"code": PermissionCode.ALERT_UPDATE_STATUS, "name": "Update Alert Status", "group": "Alert Management"},
    {"code": PermissionCode.ALERT_ACKNOWLEDGE, "name": "Acknowledge Alert", "group": "Alert Management"},

    {"code": PermissionCode.JOB_VIEW, "name": "View Job Runs", "group": "Job Orchestration"},
    {"code": PermissionCode.JOB_TRIGGER, "name": "Trigger Jobs", "group": "Job Orchestration"},

    {"code": PermissionCode.DASHBOARD_VIEW, "name": "View Dashboard", "group": "Dashboard"},
]
