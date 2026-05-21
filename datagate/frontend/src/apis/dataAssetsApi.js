import api from "./api";
export const dataAssetsApi = {
  list: (params) => api.get("/data-assets/tables", { params }),
  get: (id) => api.get(`/data-assets/tables/${id}`),
  update: (id, data) => api.put(`/data-assets/tables/${id}`, data),
  columns: (id) => api.get(`/data-assets/tables/${id}/columns`),
  processingHours: (id) => api.get(`/data-assets/tables/${id}/processing-hours`),
};

