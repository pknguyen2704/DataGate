import apiClient from './index';

export const observabilityApi = {
  // Raw data
  getSnapshots: (params) => {
    return apiClient.get('/observability/snapshots', { params });
  },
  getVolumeTS: (params) => {
    return apiClient.get('/observability/volume-ts', { params });
  },
  getSchema: (params) => {
    return apiClient.get('/observability/schema', { params });
  },
  getIncidents: (params) => {
    return apiClient.get('/observability/incidents', { params });
  },

  // Predictions (Prophet) - Simplified volume prediction for charts
  getVolumePrediction: (params) => {
    return apiClient.get('/observability/volume-prediction', { params });
  },

  // Schema change history
  getSchemaHistory: (params) => {
    return apiClient.get('/observability/schema-history', { params });
  },

  // Incident management
  resolveIncident: (incidentId) => {
    return apiClient.put(`/observability/incidents/${incidentId}/resolve`);
  },

  // Service & Config
  triggerScan: (payload) => {
    return apiClient.post('/observability/trigger-scan', payload);
  },
  getConfig: (params) => {
    return apiClient.get('/observability/config', { params });
  },
  updateConfig: (payload) => {
    return apiClient.put('/observability/config', payload);
  },
};
