import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1/profiling',
  timeout: 10000,
});

export const profilingApi = {
  // Lấy danh sách lịch sử
  getRuns: (skip = 0, limit = 20) => api.get(`/runs`, { params: { skip, limit } }),
  
  // Lấy chi tiết 1 lần chạy
  getRunDetail: (runId) => api.get(`/runs/${runId}`),
  
  // Lấy biểu đồ của 1 cột
  getColumnHistogram: (colProfileId) => api.get(`/column/${colProfileId}/histogram`),
  
  // Lấy xu hướng biến thiên
  getTrend: (table, column, metric = 'completeness') => 
    api.get(`/trend`, { params: { table, column, metric } }),
};

export default api;
