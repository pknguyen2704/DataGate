import api from "./api";

export const observabilityApi = {
  managedTree: () => api.get("/observability/managed-tree"),
  grafanaVariables: () => api.get("/observability/grafana/variables"),
  grafanaEmbedUrl: () => api.get("/observability/grafana/embed-url"),
};
