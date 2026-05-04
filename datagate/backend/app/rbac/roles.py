from app.rbac.permissions import ALL_PERMISSIONS, PermissionCode


DEFAULT_ROLE_PERMISSIONS: dict[str, list[str]] = {
    "Admin": [
        permission["code"]
        for permission in ALL_PERMISSIONS
    ],

    "Data Engineer": [
        PermissionCode.DASHBOARD_VIEW,

        PermissionCode.CONNECTION_VIEW,
        PermissionCode.CONNECTION_CREATE,
        PermissionCode.CONNECTION_UPDATE,
        PermissionCode.CONNECTION_DELETE,
        PermissionCode.CONNECTION_TEST,

        PermissionCode.TABLE_VIEW,
        PermissionCode.TABLE_CREATE,
        PermissionCode.TABLE_UPDATE,
        PermissionCode.TABLE_DELETE,

        PermissionCode.METADATA_VIEW,
        PermissionCode.METADATA_COLLECT,
        PermissionCode.OBSERVABILITY_VIEW,

        PermissionCode.RULE_VIEW,
        PermissionCode.RULE_CREATE,
        PermissionCode.RULE_UPDATE,
        PermissionCode.RULE_DELETE,
        PermissionCode.RULE_ENABLE_DISABLE,
        PermissionCode.RULE_SUGGEST,

        PermissionCode.QUALITY_VIEW,
        PermissionCode.QUALITY_RUN,

        PermissionCode.THRESHOLD_VIEW,
        PermissionCode.THRESHOLD_CREATE,
        PermissionCode.THRESHOLD_UPDATE,
        PermissionCode.THRESHOLD_DELETE,

        PermissionCode.ANOMALY_VIEW,
        PermissionCode.ANOMALY_RUN,

        PermissionCode.ALERT_VIEW,
        PermissionCode.ALERT_UPDATE_STATUS,
        PermissionCode.ALERT_ACKNOWLEDGE,

        PermissionCode.JOB_VIEW,
        PermissionCode.JOB_TRIGGER,
    ],

    "Analyst": [
        PermissionCode.DASHBOARD_VIEW,

        PermissionCode.CONNECTION_VIEW,
        PermissionCode.TABLE_VIEW,

        PermissionCode.METADATA_VIEW,
        PermissionCode.OBSERVABILITY_VIEW,

        PermissionCode.RULE_VIEW,

        PermissionCode.QUALITY_VIEW,

        PermissionCode.THRESHOLD_VIEW,

        PermissionCode.ANOMALY_VIEW,

        PermissionCode.ALERT_VIEW,

        PermissionCode.JOB_VIEW,
    ],
}