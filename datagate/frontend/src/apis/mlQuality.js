import apiClient from './index';

export const mlQualityApi = {
  getRuns: (tableName = null) => 
    apiClient.get('/ml/runs', { params: { table_name: tableName } }),
  getRunDetail: (runId) => 
    apiClient.get(`/ml/runs/${runId}`),
};
