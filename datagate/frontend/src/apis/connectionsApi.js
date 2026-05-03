import api from './api';

export const connectionsApi = {
  list: () => api.get('/connections'),
  create: (data) => api.post('/connections', data),
  get: (id) => api.get(`/connections/${id}`),
  update: (id, data) => api.patch(`/connections/${id}`, data),
  deactivate: (id) => api.patch(`/connections/${id}/deactivate`),
  delete: (id) => api.delete(`/connections/${id}`),
  test: (id) => api.post(`/connections/${id}/test`),
  listManagedTables: (id) => api.get(`/connections/${id}/managed-tables`),
  listCatalogs: (id) => api.get(`/connections/${id}/catalogs`),
  listSchemas: (id) => api.get(`/connections/${id}/schemas`),
  listTables: (id, schema) => api.get(`/connections/${id}/tables`, { params: { schema } }),
};
