import api from "./api";

export const observabilityApi = {
  getDefaultTimeRange: (tableId) => api.get(`/observability/tables/${tableId}/default-time-range`),
  getDashboardUrl: (tableId, params) => api.get(`/observability/tables/${tableId}/dashboard`, { params }),
  getManagedTree: () => api.get("/observability/managed-tree"),
  getGrafanaVariables: () => api.get("/observability/grafana/variables"),
};
