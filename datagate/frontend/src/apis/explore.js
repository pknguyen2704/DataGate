import apiClient from './index';

export const exploreApi = {
  // Discovery
  getExploreData: () => apiClient.get('/explore'),

  // Asset Overview (Metadata)
  getAssetOverview: (params) => {
    // params: { table, schema, service_id }
    return apiClient.get('/explore/overview', { params });
  },

  // Asset Sample Data
  getAssetSample: (params) => {
    // params: { table, schema, service_id, sample_limit }
    return apiClient.get('/explore/sample', { params });
  },

  // Column Stats
  getColumnStats: (params) => {
    // params: { table, schema }
    return apiClient.get('/explore/column-stats', { params });
  },
};
