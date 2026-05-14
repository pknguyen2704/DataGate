import api from "./api";

export const dataAssetsApi = {
  list: (params) => api.get("/data-assets/tables", { params }),
  create: (data) => api.post("/data-assets/tables", data),
  get: (id) => api.get(`/data-assets/tables/${id}`),
  update: (id, data) => api.put(`/data-assets/tables/${id}`, data),
  delete: (id) => api.delete(`/data-assets/tables/${id}`),
  activate: (id) => api.patch(`/data-assets/tables/${id}/activate`),
  deactivate: (id) => api.patch(`/data-assets/tables/${id}/deactivate`),
  columns: (id) => api.get(`/data-assets/tables/${id}/columns`),
  processingHours: (id) => api.get(`/data-assets/tables/${id}/processing-hours`),
};
