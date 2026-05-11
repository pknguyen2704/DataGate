import api from "./api";

export const tablesApi = {
  list: (params) => api.get("/tables", { params }),
  create: (data) => api.post("/tables", data),
  get: (id) => api.get(`/tables/${id}`),
  update: (id, data) => api.put(`/tables/${id}`, data),
  delete: (id) => api.delete(`/tables/${id}`),
  activate: (id) => api.patch(`/tables/${id}/activate`),
  deactivate: (id) => api.patch(`/tables/${id}/deactivate`),
  columns: (id) => api.get(`/tables/${id}/columns`),
  processingHours: (id) => api.get(`/tables/${id}/processing-hours`),
};
