import { PermissionCode } from "./permission";

export const Roles = {
  ADMIN: "Admin",
  ENGINEER: "Data Engineer",
  ANALYST: "Data Analyst",
};

export const DEFAULT_ROLE_PERMISSIONS = {
  [Roles.ADMIN]: Object.values(PermissionCode),
  [Roles.ENGINEER]: [
    PermissionCode.ANOMALY_CONFIG_MANAGE,
    PermissionCode.OBSERVABILITY_VIEW,
    PermissionCode.THRESHOLD_MANAGE,
    PermissionCode.RULE_MANAGE,
    PermissionCode.QUALITY_VIEW,
    PermissionCode.QUALITY_RESOLVE,
    PermissionCode.HOME_VIEW,
    PermissionCode.LAB_VIEW,
  ],
  [Roles.ANALYST]: [
    PermissionCode.OBSERVABILITY_VIEW,
    PermissionCode.THRESHOLD_MANAGE,
    PermissionCode.RULE_MANAGE,
    PermissionCode.QUALITY_VIEW,
    PermissionCode.HOME_VIEW,
    PermissionCode.LAB_VIEW,
  ],
};