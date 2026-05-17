class PermissionCode:
    # User Management (Admin only)
    USER_MANAGE = "user:manage"
    # Connections
    CONNECTION_VIEW = "connection:view"  # Admin, Engineer
    CONNECTION_MANAGE = "connection:manage"  # Admin only
    # Integrated Tables
    TABLE_VIEW = "table:view"  # All
    TABLE_MANAGE = "table:manage"  # Admin, Engineer (Add/Toggle)
    TABLE_DELETE = "table:delete"  # Admin only
    # Model Parameters
    MODEL_CONFIG_VIEW = "model_config:view"  # All
    MODEL_CONFIG_UPDATE = "model_config:update"  # Admin, Engineer
    MODEL_CONFIG_DELETE = "model_config:delete"  # Admin only
    # Metadata & Profiling
    OBSERVABILITY_VIEW = "observability:view"  # All
    # Warning Thresholds
    THRESHOLD_VIEW = "threshold:view"  # All
    THRESHOLD_MANAGE = "threshold:manage"  # Admin, Engineer
    THRESHOLD_DELETE = "threshold:delete"  # Admin only
    # Data Rules
    RULE_VIEW = "rule:view"  # All
    RULE_SUGGEST = "rule:suggest"  # All (Draft/Suggest)
    RULE_MANAGE = "rule:manage"  # Admin, Engineer (Approve/Toggle/Delete)
    # Data Quality Results
    QUALITY_VIEW = "quality:view"  # All
    QUALITY_RESOLVE = "quality:resolve"  # Admin, Engineer
    # Home
    HOME_VIEW = "home:view"  # All
    # Lab
    LAB_VIEW = "lab:view"  # All


ALL_PERMISSIONS = [
    {
        "code": PermissionCode.USER_MANAGE,
        "name": "Manage Users, Roles & Permissions",
        "group": "System Administration",
    },
    {
        "code": PermissionCode.CONNECTION_VIEW,
        "name": "View Platform Connections",
        "group": "Connection Management",
    },
    {
        "code": PermissionCode.CONNECTION_MANAGE,
        "name": "Manage Platform Connections (Add/Edit/Delete)",
        "group": "Connection Management",
    },
    {
        "code": PermissionCode.TABLE_VIEW,
        "name": "View Integrated Tables",
        "group": "Asset Management",
    },
    {
        "code": PermissionCode.TABLE_MANAGE,
        "name": "Integrate & Toggle Tables",
        "group": "Asset Management",
    },
    {
        "code": PermissionCode.TABLE_DELETE,
        "name": "Delete Table Registration",
        "group": "Asset Management",
    },
    {
        "code": PermissionCode.MODEL_CONFIG_VIEW,
        "name": "View Model Parameters",
        "group": "Model Configuration",
    },
    {
        "code": PermissionCode.MODEL_CONFIG_UPDATE,
        "name": "Update Model Parameters",
        "group": "Model Configuration",
    },
    {
        "code": PermissionCode.MODEL_CONFIG_DELETE,
        "name": "Delete Model Parameters",
        "group": "Model Configuration",
    },
    {
        "code": PermissionCode.OBSERVABILITY_VIEW,
        "name": "View Metadata & Profiling",
        "group": "Observability",
    },
    {
        "code": PermissionCode.THRESHOLD_VIEW,
        "name": "View Warning Thresholds",
        "group": "Quality Configuration",
    },
    {
        "code": PermissionCode.THRESHOLD_MANAGE,
        "name": "Manage Warning Thresholds (Add/Edit)",
        "group": "Quality Configuration",
    },
    {
        "code": PermissionCode.THRESHOLD_DELETE,
        "name": "Delete Warning Thresholds",
        "group": "Quality Configuration",
    },
    {
        "code": PermissionCode.RULE_VIEW,
        "name": "View Data Rules",
        "group": "Rule Management",
    },
    {
        "code": PermissionCode.RULE_SUGGEST,
        "name": "Suggest & Draft Rules",
        "group": "Rule Management",
    },
    {
        "code": PermissionCode.RULE_MANAGE,
        "name": "Manage Rules (Approve/Toggle/Delete)",
        "group": "Rule Management",
    },
    {
        "code": PermissionCode.QUALITY_VIEW,
        "name": "View Data Quality Results",
        "group": "Quality Operations",
    },
    {
        "code": PermissionCode.QUALITY_RESOLVE,
        "name": "Resolve Quality Issues",
        "group": "Quality Operations",
    },
    {
        "code": PermissionCode.HOME_VIEW,
        "name": "View Home Dashboard",
        "group": "Observability",
    },
    {"code": PermissionCode.LAB_VIEW, "name": "View Jupiter Notebook", "group": "Lab"},
]
