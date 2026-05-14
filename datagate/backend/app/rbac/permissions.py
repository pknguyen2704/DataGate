class PermissionCode:
    ADMIN = "admin"

    USER_VIEW = "user:view"
    USER_CREATE = "user:create"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    USER_MANAGE = "user:manage"

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
    CONNECTION_MANAGE = "connection:manage"

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

    MODEL_CONFIG_VIEW = "model_config:view"
    MODEL_CONFIG_MANAGE = "model_config:manage"

    DASHBOARD_VIEW = "dashboard:view"
    HOME_VIEW = "home:view"


ALL_PERMISSIONS = [
    {"code": PermissionCode.ADMIN, "name": "System Administrator (Super Admin)", "group": "System"},

    {"code": PermissionCode.USER_VIEW, "name": "View Users", "group": "User Management"},
    {"code": PermissionCode.USER_CREATE, "name": "Create User", "group": "User Management"},
    {"code": PermissionCode.USER_UPDATE, "name": "Update User", "group": "User Management"},
    {"code": PermissionCode.USER_DELETE, "name": "Delete User", "group": "User Management"},
    {"code": PermissionCode.USER_MANAGE, "name": "Manage Users, Roles and Permissions", "group": "User Management"},

    {"code": PermissionCode.ROLE_VIEW, "name": "View Roles", "group": "User Management"},
    {"code": PermissionCode.ROLE_CREATE, "name": "Create Role", "group": "User Management"},
    {"code": PermissionCode.ROLE_UPDATE, "name": "Update Role", "group": "User Management"},
    {"code": PermissionCode.ROLE_DELETE, "name": "Delete Role", "group": "User Management"},
    {"code": PermissionCode.ROLE_ASSIGN_PERMISSION, "name": "Assign Permissions to Role", "group": "User Management"},

    {"code": PermissionCode.CONNECTION_VIEW, "name": "View Connections", "group": "Data Connection Management"},
    {"code": PermissionCode.CONNECTION_CREATE, "name": "Create Connection", "group": "Data Connection Management"},
    {"code": PermissionCode.CONNECTION_UPDATE, "name": "Update Connection", "group": "Data Connection Management"},
    {"code": PermissionCode.CONNECTION_DELETE, "name": "Disable/Delete Connection", "group": "Data Connection Management"},
    {"code": PermissionCode.CONNECTION_TEST, "name": "Test Connection", "group": "Data Connection Management"},
    {"code": PermissionCode.CONNECTION_MANAGE, "name": "Manage System Connections", "group": "Data Connection Management"},

    {"code": PermissionCode.TABLE_VIEW, "name": "View Table List", "group": "Metadata & Profiling"},
    {"code": PermissionCode.TABLE_CREATE, "name": "Register New Table", "group": "Metadata & Profiling"},
    {"code": PermissionCode.TABLE_UPDATE, "name": "Update Table Info", "group": "Metadata & Profiling"},
    {"code": PermissionCode.TABLE_DELETE, "name": "Delete Table Registration", "group": "Metadata & Profiling"},

    {"code": PermissionCode.METADATA_VIEW, "name": "View Metadata", "group": "Metadata & Profiling"},
    {"code": PermissionCode.METADATA_COLLECT, "name": "Collect Metadata", "group": "Metadata & Profiling"},
    {"code": PermissionCode.OBSERVABILITY_VIEW, "name": "View Data Observability", "group": "Metadata & Profiling"},

    {"code": PermissionCode.RULE_VIEW, "name": "View Data Rules", "group": "Data Rule Management"},
    {"code": PermissionCode.RULE_CREATE, "name": "Create Draft Rule", "group": "Data Rule Management"},
    {"code": PermissionCode.RULE_UPDATE, "name": "Update Draft Rule", "group": "Data Rule Management"},
    {"code": PermissionCode.RULE_DELETE, "name": "Delete Data Rule", "group": "Data Rule Management"},
    {"code": PermissionCode.RULE_ENABLE_DISABLE, "name": "Approve & Enable/Disable Rules", "group": "Data Rule Management"},
    {"code": PermissionCode.RULE_SUGGEST, "name": "Suggest Automatic Rules", "group": "Data Rule Management"},

    {"code": PermissionCode.QUALITY_VIEW, "name": "View Data Quality Results", "group": "Data Quality Management"},
    {"code": PermissionCode.QUALITY_RUN, "name": "Update Resolution Status (Resolve)", "group": "Data Quality Management"},

    {"code": PermissionCode.THRESHOLD_VIEW, "name": "View Warning Thresholds", "group": "Threshold Management"},
    {"code": PermissionCode.THRESHOLD_CREATE, "name": "Create Warning Threshold", "group": "Threshold Management"},
    {"code": PermissionCode.THRESHOLD_UPDATE, "name": "Update Warning Threshold", "group": "Threshold Management"},
    {"code": PermissionCode.THRESHOLD_DELETE, "name": "Delete Warning Threshold", "group": "Threshold Management"},

    {"code": PermissionCode.ANOMALY_VIEW, "name": "View Anomaly Detection Results", "group": "Anomaly Detection Management"},
    {"code": PermissionCode.ANOMALY_RUN, "name": "Run Anomaly Detection", "group": "Anomaly Detection Management"},

    {"code": PermissionCode.ALERT_VIEW, "name": "View Alerts", "group": "System"},
    {"code": PermissionCode.ALERT_UPDATE_STATUS, "name": "Update Alert Status", "group": "System"},

    {"code": PermissionCode.JOB_VIEW, "name": "View Schedules (Jobs)", "group": "System"},
    {"code": PermissionCode.JOB_TRIGGER, "name": "Trigger Job Manually", "group": "System"},

    {"code": PermissionCode.MODEL_CONFIG_VIEW, "name": "View Model Parameters", "group": "Model Parameter Management"},
    {"code": PermissionCode.MODEL_CONFIG_MANAGE, "name": "Manage Model Parameters", "group": "Model Parameter Management"},

    {"code": PermissionCode.DASHBOARD_VIEW, "name": "View Monitoring Dashboard", "group": "Dashboard/Grafana"},
    {"code": PermissionCode.HOME_VIEW, "name": "View System Summary (Home)", "group": "Dashboard/Grafana"},
]
