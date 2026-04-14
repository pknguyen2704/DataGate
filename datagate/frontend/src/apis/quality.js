import apiClient from './index';

export const qualityApi = {
  getRuns: (tableName = null) => 
    apiClient.get('/quality/runs', { params: { table_name: tableName } }),
  getRunDetail: (runId) => 
    apiClient.get(`/quality/runs/${runId}`),
};
