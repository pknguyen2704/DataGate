from app.rbac.permissions import ALL_PERMISSIONS, PermissionCode


DEFAULT_ROLE_PERMISSIONS: dict[str, list[str]] = {
    "Admin": [
        permission["code"]
        for permission in ALL_PERMISSIONS
    ],

    "Data Engineer": [
        PermissionCode.DASHBOARD_VIEW,
        PermissionCode.HOME_VIEW,
        PermissionCode.CONNECTION_VIEW,
        PermissionCode.CONNECTION_TEST,
        # Cannot create, update, or delete connections (Admin only)
        PermissionCode.TABLE_VIEW,
        PermissionCode.TABLE_CREATE,
        PermissionCode.TABLE_UPDATE,
        # Cannot delete tables
        PermissionCode.METADATA_VIEW,
        PermissionCode.METADATA_COLLECT,
        PermissionCode.OBSERVABILITY_VIEW,
        PermissionCode.RULE_VIEW,
        PermissionCode.RULE_CREATE,
        PermissionCode.RULE_UPDATE,
        # Cannot delete rules
        PermissionCode.RULE_ENABLE_DISABLE,
        PermissionCode.RULE_SUGGEST,
        PermissionCode.QUALITY_VIEW,
        PermissionCode.QUALITY_RUN,
        PermissionCode.THRESHOLD_VIEW,
        PermissionCode.THRESHOLD_CREATE,
        PermissionCode.THRESHOLD_UPDATE,
        # Cannot delete thresholds
        PermissionCode.ANOMALY_VIEW,
        PermissionCode.ANOMALY_RUN,
        PermissionCode.ALERT_VIEW,
        PermissionCode.ALERT_UPDATE_STATUS,
        PermissionCode.ALERT_ACKNOWLEDGE,
        PermissionCode.JOB_VIEW,
        PermissionCode.JOB_TRIGGER,
        PermissionCode.MODEL_CONFIG_VIEW,
        PermissionCode.MODEL_CONFIG_MANAGE,
    ],

    "Data Analyst": [
        PermissionCode.DASHBOARD_VIEW,
        PermissionCode.HOME_VIEW,
        PermissionCode.TABLE_VIEW,
        PermissionCode.METADATA_VIEW,
        PermissionCode.OBSERVABILITY_VIEW,
        PermissionCode.RULE_VIEW,
        PermissionCode.RULE_CREATE,
        PermissionCode.RULE_UPDATE,
        PermissionCode.QUALITY_VIEW,
        PermissionCode.THRESHOLD_VIEW,
        PermissionCode.ANOMALY_VIEW,
        PermissionCode.ALERT_VIEW,
        PermissionCode.JOB_VIEW,
        PermissionCode.MODEL_CONFIG_VIEW,
    ],
}