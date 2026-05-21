import api from "./api";

export const observabilityApi = {
  getDefaultTimeRange: (tableId) => api.get(`/observability/tables/${tableId}/default-time-range`),
  getObservabilityUrl: (tableId, params) => api.get(`/observability/tables/${tableId}/observability`, { params }),
  getObservabilityVariables: () => api.get("/observability/variables"),
};
