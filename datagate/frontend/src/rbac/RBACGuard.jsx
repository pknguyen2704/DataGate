import React from "react";
import { useRBAC } from "./useRBAC";

export const RBACGuard = ({
  permission,
  permissions,
  requireAll = false,
  fallback = null,
  children,
}) => {
  const { hasPermission, hasAnyPermission, hasAllPermissions } = useRBAC();

  let allowed = false;

  if (permission) {
    allowed = hasPermission(permission);
  } else if (permissions) {
    allowed = requireAll ? hasAllPermissions(permissions) : hasAnyPermission(permissions);
  } else {
    allowed = true; // No restriction
  }

  if (!allowed) {
    return fallback;
  }

  return <>{children}</>;
};

export default RBACGuard;
