import apiClient from './index';

export const rulesApi = {
  getRules: (table) => apiClient.get('/rules', { params: { table } }),
  createRule: (data) => apiClient.post('/rules', data),
  updateRule: (id, data) => apiClient.patch(`/rules/${id}`, data),
  deleteRule: (id) => apiClient.delete(`/rules/${id}`),
  triggerSuggestions: (data) => apiClient.post('/rules/suggestions/trigger', data),
  triggerValidation: (data) => apiClient.post('/rules/validate/trigger', data),
};
