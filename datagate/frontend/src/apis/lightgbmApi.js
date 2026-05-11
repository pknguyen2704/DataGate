import api from "./api";

export const lightgbmApi = {
  parameters: () => api.get("/lightgbm/parameters"),
  create: (data) => api.post("/lightgbm/parameters", data),
  get: (id) => api.get(`/lightgbm/parameters/${id}`),
  update: (id, data) => api.put(`/lightgbm/parameters/${id}`, data),
  delete: (id) => api.delete(`/lightgbm/parameters/${id}`),
  validateJson: (data) => api.post("/lightgbm/parameters/validate-json", data),
  importJson: (data) => api.post("/lightgbm/parameters/import-json", data),
  tableParameters: (tableId) => api.get(`/lightgbm/tables/${tableId}/parameters`),
};
