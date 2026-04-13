import api from './services';

export const rulesApi = {
  getRules: (table) => api.get('/rules', { params: { table } }),
  createRule: (data) => api.post('/rules', data),
  updateRule: (id, data) => api.patch(`/rules/${id}`, data),
  deleteRule: (id) => api.delete(`/rules/${id}`),
};
