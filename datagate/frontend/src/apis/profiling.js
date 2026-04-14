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
};

export default apiClient;
