import apiClient from './index';

export const observabilityApi = {
  // Raw data
  getSnapshots: (params) => {
    // params: { table, schema }
    return apiClient.get('/observability/snapshots', { params });
  },
  getVolumeTS: (params) => {
    // params: { table, schema }
    return apiClient.get('/observability/volume-ts', { params });
  },
  getSchema: (params) => {
    // params: { table, schema }
    return apiClient.get('/observability/schema', { params });
  },
  getIncidents: (params) => {
    // params: { table, schema }
    return apiClient.get('/observability/incidents', { params });
  },
  getMetrics: (params) => {
    // params: { table, schema, column }
    return apiClient.get('/observability/metrics', { params });
  },
  getMetricPredictions: (params) => {
    // params: { table, schema, column, metric }
    return apiClient.get('/observability/metric-predictions', { params });
  },

  // Predictions (Prophet)
  getVolumePrediction: (params) => {
    // params: { table, schema }
    return apiClient.get('/observability/volume-prediction', { params });
  },
  getFreshnessPrediction: (params) => {
    // params: { table, schema }
    return apiClient.get('/observability/freshness-prediction', { params });
  },

  // Schema change history
  getSchemaHistory: (params) => {
    // params: { table, schema }
    return apiClient.get('/observability/schema-history', { params });
  },

  // Incident management
  resolveIncident: (incidentId) => {
    return apiClient.put(`/observability/incidents/${incidentId}/resolve`);
  },

  // Service actions
  triggerScan: (payload) => {
    return apiClient.post('/observability/trigger-scan', payload);
  },
  getConfig: (params) => {
    return apiClient.get('/observability/config', { params });
  },
  updateConfig: (payload) => {
    return apiClient.put('/observability/config', payload);
  },
  refreshTables: (serviceId) => {
    return apiClient.post(`/observability/services/${serviceId}/refresh-tables`);
  },
  scanService: (serviceId) => {
    return apiClient.post(`/observability/services/${serviceId}/scan`);
  },
};
