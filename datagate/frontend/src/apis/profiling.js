import apiClient from './index';

export const profilingApi = {
  // Lấy danh sách lịch sử
  getRuns: (skip = 0, limit = 20) => apiClient.get(`/profiling/runs`, { params: { skip, limit } }),
  
  // Lấy chi tiết 1 lần chạy
  getRunDetail: (runId) => apiClient.get(`/profiling/runs/${runId}`),
  
  // Lấy biểu đồ của 1 cột
  getColumnHistogram: (colProfileId) => apiClient.get(`/profiling/column/${colProfileId}/histogram`),
  
  // Lấy xu hướng biến thiên
  getTrend: (table, column, metric = 'completeness') => 
    apiClient.get(`/profiling/trend`, { params: { table, column, metric } }),

  getMonitoringRecommendations: (table) =>
    apiClient.get(`/profiling/monitoring/recommendations`, { params: { table } }),

  getMonitoringSeries: (table, column, metric = "null_rate", confidence = 95) =>
    apiClient.get(`/profiling/monitoring/series`, { params: { table, column, metric, confidence } }),
};

export default apiClient;
