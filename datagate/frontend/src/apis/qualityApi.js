import api from "./api";

export const qualityApi = {
  summary: () => api.get("/quality/summary"),
  results: (params) => api.get("/quality/results", { params }),
  metadata: () => api.get("/quality/metadata-results"),
  profiling: () => api.get("/quality/profiling-results"),
  rule: () => api.get("/quality/rule-results"),
  anomaly: () => api.get("/quality/anomaly-results"),
  unresolved: () => api.get("/quality/unresolved-failures"),
};
