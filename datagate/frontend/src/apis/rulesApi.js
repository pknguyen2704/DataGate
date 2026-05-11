import api from './api';

export const rulesApi = {
  list: (params) => api.get('/rules', { params }),
  listVerifications: (params) => api.get('/rules/verify-results', { params }),
  create: (data) => api.post('/rules', data),
  get: (id) => api.get(`/rules/${id}`),
  update: (id, data) => api.put(`/rules/${id}`, data),
  activate: (id) => api.patch(`/rules/${id}/activate`),
  inactive: (id) => api.patch(`/rules/${id}/inactive`),
  resolve: (id) => api.patch(`/rules/verify-results/${id}/resolve`),
  unresolve: (id) => api.patch(`/rules/verify-results/${id}/unresolve`),
  managedTables: () => api.get('/rules/managed-tables'),
  delete: (id) => api.delete(`/rules/${id}`),
};
