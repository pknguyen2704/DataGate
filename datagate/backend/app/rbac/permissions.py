class PermissionCode:
    USER_MANAGE = "user:manage"              # Admin
    CONNECTION_MANAGE = "connection:manage"  # Admin only
    MODEL_CONFIG_VIEW = "model_config:view"  # All
    MODEL_CONFIG_MANAGE = "model_config:manage"  # Admin, Engineer
    # Metadata & Profiling
    OBSERVABILITY_VIEW = "observability:view"  # All
    # Warning Thresholds
    THRESHOLD_VIEW = "threshold:view"        # All
    THRESHOLD_MANAGE = "threshold:manage"    # Admin, Engineer
    # Data Rules
    RULE_VIEW = "rule:view"                  # All
    RULE_MANAGE = "rule:manage"              # All (Create/Update/Approve/Deactivate/Delete)
    # Data Quality Results
    QUALITY_VIEW = "quality:view"            # All
    QUALITY_RESOLVE = "quality:resolve"      # Admin, Engineer
    HOME_VIEW = "home:view"                  # All
    LAB_VIEW = "lab:view"                    # All


ALL_PERMISSIONS = [
    {
        "code": PermissionCode.USER_MANAGE,
        "name": "Manage Users",
        "group": "System Administration",
    },
    {
        "code": PermissionCode.CONNECTION_MANAGE,
        "name": "Manage Platform Connections (Create/Update/Delete/Table Registration)",
        "group": "Connection Management",
    },
    {
        "code": PermissionCode.MODEL_CONFIG_VIEW,
        "name": "View Model Parameters",
        "group": "Model Configuration",
    },
    {
        "code": PermissionCode.MODEL_CONFIG_MANAGE,
        "name": "Manage Model Parameters (Create/Update/Delete)",
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
        "name": "Manage Warning Thresholds (Create/Update/Delete)",
        "group": "Quality Configuration",
    },
    {
        "code": PermissionCode.RULE_VIEW,
        "name": "View Data Rules",
        "group": "Rule Management",
    },
    {
        "code": PermissionCode.RULE_MANAGE,
        "name": "Manage Rules (Create/Update/Approve/Deactivate/Delete)",
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
    {
        "code": PermissionCode.LAB_VIEW,
        "name": "View Jupyter Notebook",
        "group": "Lab",
    },
]
