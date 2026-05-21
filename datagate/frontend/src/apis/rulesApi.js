import api from "./api";

export const rulesApi = {
  list: (params) => api.get("/rules", { params }),
  get: (id) => api.get(`/rules/${id}`),
  create: (data) => api.post("/rules", data),
  update: (id, data) => api.patch(`/rules/${id}`, data),
  delete: (id) => api.delete(`/rules/${id}`),
  approve: (id) => api.post(`/rules/${id}/approve`),
  deactivate: (id) => api.post(`/rules/${id}/deactivate`),
};
