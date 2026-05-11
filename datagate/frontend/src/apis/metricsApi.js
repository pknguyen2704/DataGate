import api from "./api";

const path = {
  metadata: "/metrics/metadata-thresholds",
  profiling: "/metrics/profiling-thresholds",
  auc: "/metrics/auc-thresholds",
};

export const metricsApi = {
  list: (type, params) => api.get(path[type], { params }),
  create: (type, data) => api.post(path[type], data),
  update: (type, id, data) => api.put(`${path[type]}/${id}`, data),
  delete: (type, id) => api.delete(`${path[type]}/${id}`),
  activate: (type, id) => api.patch(`${path[type]}/${id}/activate`),
  deactivate: (type, id) => api.patch(`${path[type]}/${id}/deactivate`),
};
