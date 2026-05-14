import api from "./api";

const BASE_URL = "/settings/roles";

export const rolesApi = {
  list: () => api.get(BASE_URL),
  create: (data) => api.post(BASE_URL, data),
  get: (id) => api.get(`${BASE_URL}/${id}`),
  update: (id, data) => api.patch(`${BASE_URL}/${id}`, data),
  delete: (id) => api.delete(`${BASE_URL}/${id}`),
  assignPermissions: (id, permissionIds) => api.patch(`${BASE_URL}/${id}/permissions`, { permission_ids: permissionIds }),
  
  // Permissions helper
  listPermissions: () => api.get("/settings/permissions"),
  listPermissionsGrouped: () => api.get("/settings/permissions/grouped"),
};
