import { useSelector } from "react-redux";
import { useCallback } from "react";
import { PermissionCode } from "./permission";

export const useRBAC = () => {
  const { user, isAuthenticated, loading } = useSelector((state) => state.auth);
  const permissions = user?.permissions || [];
  const roles = user?.roles || [];

  const hasRole = useCallback((roleName) => {
    return roles.some((r) => {
      if (typeof r === "string") return r === roleName;
      return r?.name === roleName;
    });
  }, [roles]);

  const isAdmin = hasRole("Admin");

  const hasPermission = useCallback((permissionCode) => {
    if (!isAuthenticated || !user) return false;
    if (isAdmin) return true;
    if (!permissionCode) return true;

    return permissions.some((p) => {
      if (typeof p === "string") return p === permissionCode;
      return p?.code === permissionCode;
    });
  }, [isAuthenticated, user, isAdmin, permissions]);

  const hasAnyPermission = useCallback((permissionCodes) => {
    if (!permissionCodes || permissionCodes.length === 0) return true;
    return permissionCodes.some((code) => hasPermission(code));
  }, [hasPermission]);

  const hasAllPermissions = useCallback((permissionCodes) => {
    if (!permissionCodes || permissionCodes.length === 0) return true;
    return permissionCodes.every((code) => hasPermission(code));
  }, [hasPermission]);

  return {
    user,
    isAuthenticated,
    loading,
    roles,
    permissions,
    isAdmin,
    hasRole,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
  };
};
