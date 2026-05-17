import api from "./api";

export const observabilityApi = {
  getDefaultTimeRange: (tableId) => api.get(`/observability/tables/${tableId}/default-time-range`),
  getObservabilityUrl: (tableId, params) => api.get(`/observability/tables/${tableId}/observability`, { params }),
  getManagedTree: () => api.get("/observability/managed-tree"),
  getObservabilityVariables: () => api.get("/observability/variables"),
};
