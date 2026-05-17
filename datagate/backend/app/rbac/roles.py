from app.rbac.permissions import ALL_PERMISSIONS, PermissionCode


DEFAULT_ROLE_PERMISSIONS: dict[str, list[str]] = {
    "Admin": [permission["code"] for permission in ALL_PERMISSIONS],
    "Data Engineer": [
        PermissionCode.CONNECTION_VIEW,
        PermissionCode.TABLE_VIEW,
        PermissionCode.TABLE_MANAGE,
        PermissionCode.MODEL_CONFIG_VIEW,
        PermissionCode.MODEL_CONFIG_UPDATE,
        PermissionCode.OBSERVABILITY_VIEW,
        PermissionCode.THRESHOLD_VIEW,
        PermissionCode.THRESHOLD_MANAGE,
        PermissionCode.RULE_VIEW,
        PermissionCode.RULE_SUGGEST,
        PermissionCode.RULE_MANAGE,
        PermissionCode.QUALITY_VIEW,
        PermissionCode.QUALITY_RESOLVE,
        PermissionCode.HOME_VIEW,
        PermissionCode.LAB_VIEW,
    ],
    "Data Analyst": [
        PermissionCode.TABLE_VIEW,
        PermissionCode.MODEL_CONFIG_VIEW,
        PermissionCode.OBSERVABILITY_VIEW,
        PermissionCode.THRESHOLD_VIEW,
        PermissionCode.RULE_VIEW,
        PermissionCode.RULE_SUGGEST,
        PermissionCode.QUALITY_VIEW,
        PermissionCode.HOME_VIEW,
        PermissionCode.LAB_VIEW,
    ],
}
