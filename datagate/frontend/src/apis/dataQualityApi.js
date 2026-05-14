import api from "./api";

export const dataQualityApi = {
  listResults: (params) => api.get("/data-quality/results", { params }),
  getSummary: (params) => api.get("/data-quality/results/summary", { params }),
  
  getMetadataDetail: (id) => api.get(`/data-quality/metadata-results/${id}`),
  resolveMetadata: (id) => api.patch(`/data-quality/metadata-results/${id}/resolve`),
  
  getProfilingDetail: (id) => api.get(`/data-quality/profiling-results/${id}`),
  resolveProfiling: (id) => api.patch(`/data-quality/profiling-results/${id}/resolve`),
  
  getRuleDetail: (id) => api.get(`/data-quality/rule-results/${id}`),
  resolveRule: (id) => api.patch(`/data-quality/rule-results/${id}/resolve`),
  
  getAnomalyDetail: (id) => api.get(`/data-quality/anomaly-results/${id}`),
  resolveAnomaly: (id) => api.patch(`/data-quality/anomaly-results/${id}/resolve`),
};
