import { PermissionCode } from "./permission";

export const Roles = {
  ADMIN: "Admin",
  ENGINEER: "Data Engineer",
  ANALYST: "Data Analyst",
};

export const DEFAULT_ROLE_PERMISSIONS = {
  [Roles.ADMIN]: Object.values(PermissionCode),
  [Roles.ENGINEER]: [
    PermissionCode.MODEL_CONFIG_VIEW,
    PermissionCode.MODEL_CONFIG_MANAGE,
    PermissionCode.OBSERVABILITY_VIEW,
    PermissionCode.THRESHOLD_VIEW,
    PermissionCode.THRESHOLD_MANAGE,
    PermissionCode.RULE_VIEW,
    PermissionCode.RULE_MANAGE,
    PermissionCode.QUALITY_VIEW,
    PermissionCode.QUALITY_RESOLVE,
    PermissionCode.HOME_VIEW,
    PermissionCode.LAB_VIEW,
  ],
  [Roles.ANALYST]: [
    PermissionCode.MODEL_CONFIG_VIEW,
    PermissionCode.OBSERVABILITY_VIEW,
    PermissionCode.THRESHOLD_VIEW,
    PermissionCode.RULE_VIEW,
    PermissionCode.RULE_MANAGE,
    PermissionCode.QUALITY_VIEW,
    PermissionCode.HOME_VIEW,
    PermissionCode.LAB_VIEW,
  ],
};