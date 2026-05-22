from app.rbac.permissions import ALL_PERMISSIONS, PermissionCode


DEFAULT_ROLE_PERMISSIONS: dict[str, list[str]] = {
    "Admin": [permission["code"] for permission in ALL_PERMISSIONS],
    "Data Engineer": [
        PermissionCode.ANOMALY_CONFIG_MANAGE,
        PermissionCode.OBSERVABILITY_VIEW,
        PermissionCode.THRESHOLD_MANAGE,
        PermissionCode.RULE_MANAGE,
        PermissionCode.QUALITY_VIEW,
        PermissionCode.QUALITY_RESOLVE,
        PermissionCode.HOME_VIEW,
        PermissionCode.LAB_VIEW,
    ],
    "Data Analyst": [
        PermissionCode.OBSERVABILITY_VIEW,
        PermissionCode.THRESHOLD_MANAGE,
        PermissionCode.RULE_MANAGE,
        PermissionCode.QUALITY_VIEW,
        PermissionCode.HOME_VIEW,
        PermissionCode.LAB_VIEW,
    ],
}
