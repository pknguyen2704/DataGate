import api from './api';

export const rulesApi = {
  list: (params) => api.get('/rules', { params }),
  listVerifications: (params) => api.get('/rules/verifications', { params }),
  create: (data) => api.post('/rules', data),
  get: (id) => api.get(`/rules/${id}`),
  update: (id, data) => api.patch(`/rules/${id}`, data),
  updateStatus: (id, status) => api.patch(`/rules/${id}/status`, { status }),
  delete: (id) => api.delete(`/rules/${id}`),
};
