import api from "./api";
export const connectionsApi = {
  list: (params) => api.get("/connections", { params }),
  create: (data) => api.post("/connections", data),
  get: (id) => api.get(`/connections/${id}`),
  update: (id, data) => api.patch(`/connections/${id}`, data),
  activate: (id) => api.patch(`/connections/${id}/activate`),
  deactivate: (id) => api.patch(`/connections/${id}/deactivate`),
  delete: (id) => api.delete(`/connections/${id}`),
  test: (id) => api.post(`/connections/${id}/test`),
  listCatalogs: (id) => api.get(`/connections/${id}/catalogs`),
  listSchemas: (id) => api.get(`/connections/${id}/schemas`),
  listTables: (id, params) => api.get(`/connections/${id}/tables`, { params }),
  listManagedTables: (id) => api.get(`/connections/${id}/managed-tables`),
};
