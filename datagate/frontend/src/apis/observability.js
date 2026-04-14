import apiClient from './index';

export const observabilityApi = {
  getJobs: () => apiClient.get('/observability/jobs'),
  createJob: (data) => apiClient.post('/observability/jobs', data),
  triggerJob: (jobId) => apiClient.post(`/observability/jobs/${jobId}/trigger`),
  triggerScan: (data) => apiClient.post('/observability/trigger-scan', data),
  getSnapshots: (tableName) => apiClient.get('/observability/snapshots', { params: { table_name: tableName } }),
  getVolumeTS: (tableName) => apiClient.get('/observability/volume-ts', { params: { table_name: tableName } }),
  getIncidents: (tableName) => apiClient.get('/observability/incidents', { params: { table_name: tableName } }),
  getSchema: (tableName) => apiClient.get('/observability/schema', { params: { table_name: tableName } }),
  getColumnStats: (tableName) => apiClient.get('/observability/column-stats', { params: { table_name: tableName } }),
  triggerMLScan: (data) => apiClient.post('/observability/ml-trigger', data),
};
