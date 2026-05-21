import api from "./api";

const BASE_URL = "/settings/connections";

export const connectionsApi = {
  list: (params) => api.get(BASE_URL, { params }),
  create: (data) => api.post(BASE_URL, data),
  get: (id) => api.get(`${BASE_URL}/${id}`),
  update: (id, data) => api.patch(`${BASE_URL}/${id}`, data),
  delete: (id) => api.delete(`${BASE_URL}/${id}`),
  activate: (id) => api.post(`${BASE_URL}/${id}/activate`),
  deactivate: (id) => api.post(`${BASE_URL}/${id}/deactivate`),

  // Table Discovery
  discover: (id, schema) => api.get(`${BASE_URL}/${id}/discover-tables`, { params: { schema } }),
  
  // Managed Tables
  addManagedTable: (id, data) => api.post(`${BASE_URL}/${id}/managed-tables`, null, { params: data }),
  removeManagedTable: (id, tableId) => api.delete(`${BASE_URL}/${id}/managed-tables/${tableId}`),
};
