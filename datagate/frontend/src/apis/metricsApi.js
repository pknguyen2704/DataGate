import api from "./api";

export const metricsApi = {
  // Metadata Thresholds
  listMetadata: (tableId) => api.get("/metrics/metadata-thresholds", { params: { table_id: tableId } }),
  getMetadata: (id) => api.get(`/metrics/metadata-thresholds/${id}`),
  createMetadata: (data) => api.post("/metrics/metadata-thresholds", data),
  updateMetadata: (id, data) => api.patch(`/metrics/metadata-thresholds/${id}`, data),
  deleteMetadata: (id) => api.delete(`/metrics/metadata-thresholds/${id}`),

  // Profiling Thresholds
  listProfiling: (tableId) => api.get("/metrics/profiling-thresholds", { params: { table_id: tableId } }),
  getProfiling: (id) => api.get(`/metrics/profiling-thresholds/${id}`),
  createProfiling: (data) => api.post("/metrics/profiling-thresholds", data),
  updateProfiling: (id, data) => api.patch(`/metrics/profiling-thresholds/${id}`, data),
  deleteProfiling: (id) => api.delete(`/metrics/profiling-thresholds/${id}`),

  // Anomaly Thresholds
  listAnomaly: (tableId) => api.get("/metrics/anomaly-thresholds", { params: { table_id: tableId } }),
  getAnomaly: (id) => api.get(`/metrics/anomaly-thresholds/${id}`),
  createAnomaly: (data) => api.post("/metrics/anomaly-thresholds", data),
  updateAnomaly: (id, data) => api.patch(`/metrics/anomaly-thresholds/${id}`, data),
  deleteAnomaly: (id) => api.delete(`/metrics/anomaly-thresholds/${id}`),
};
