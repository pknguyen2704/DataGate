import api from './api';

export const rolesApi = {
  list: () => api.get('/roles'),
  create: (data) => api.post('/roles', data),
  get: (id) => api.get(`/roles/${id}`),
  update: (id, data) => api.patch(`/roles/${id}`, data),
  delete: (id) => api.delete(`/roles/${id}`),
  assignPermissions: (id, permIds) => api.post(`/roles/${id}/permissions`, { permission_ids: permIds }),
  listPermissions: () => api.get('/roles/permissions'),
};
