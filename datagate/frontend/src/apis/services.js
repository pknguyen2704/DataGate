import apiClient from './index';

export const servicesApi = {
  getServices: () => apiClient.get('/services'),
  createService: (data) => apiClient.post('/services', data),
  testConnection: (data) => apiClient.post('/services/test', data),
  getServiceSchemas: (serviceId) => apiClient.get(`/services/${serviceId}/schemas`),
  getServiceTables: (serviceId, schema = null) => apiClient.get(`/services/${serviceId}/tables`, { params: { schema } }),
  getSchemaTablesRaw: (serviceType, url, schema) => apiClient.get('/services/raw/tables', { params: { service_type: serviceType, url, schema } }),
  refreshTables: (serviceId) => apiClient.post(`/services/${serviceId}/refresh-tables`),
  deleteService: (serviceId) => apiClient.delete(`/services/${serviceId}`),
  updateService: (serviceId, data) => apiClient.put(`/services/${serviceId}`, data),
};

export default apiClient;
