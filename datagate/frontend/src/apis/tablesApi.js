import api from "./api";

export const tablesApi = {
  list: (params) => api.get("/tables", { params }),
  create: (data) => api.post("/tables", data),
  get: (id) => api.get(`/tables/${id}`),
  update: (id, data) => api.patch(`/tables/${id}`, data),
  delete: (id) => api.delete(`/tables/${id}`),
  deactivate: (id) => api.patch(`/tables/${id}/deactivate`),
  grantAccess: (id, data) => api.post(`/tables/${id}/accesses`, data),
  revokeAccess: (id, userId) =>
    api.delete(`/tables/${id}/accesses/${userId}`),
  getMetadata: (id, params) =>
    api.get(`/tables/${id}/metadata`, { params }),
  getAnomalies: (id, params) =>
    api.get(`/tables/${id}/anomalies`, { params }),
  getRules: (id, params) =>
    api.get(`/tables/${id}/rules`, { params }),
  getSample: (id, params) =>
    api.get(`/tables/${id}/sample`, { params }),
};