import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 10000,
});

export const servicesApi = {
  getServices: () => api.get('/services'),
  createService: (data) => api.post('/services', data),
  testConnection: (data) => api.post('/services/test', data),
  getServiceSchemas: (serviceId) => api.get(`/services/${serviceId}/schemas`),
  getServiceTables: (serviceId, schema = null) => api.get(`/services/${serviceId}/tables`, { params: { schema } }),
  getSchemaTablesRaw: (serviceType, url, schema) => api.get('/services/raw/tables', { params: { service_type: serviceType, url, schema } }),
  deleteService: (serviceId) => api.delete(`/services/${serviceId}`),
};

export default api;
