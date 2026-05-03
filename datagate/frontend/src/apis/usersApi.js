import api from './api';

export const usersApi = {
  list: (params) => api.get('/users', { params }),
  create: (data) => api.post('/users', data),
  get: (id) => api.get(`/users/${id}`),
  update: (id, data) => api.patch(`/users/${id}`, data),
  deactivate: (id) => api.delete(`/users/${id}`),
  assignRoles: (id, roleIds) => api.post(`/users/${id}/roles`, roleIds),
  getMe: () => api.get('/users/me'),
  updateMe: (data) => api.patch('/users/me', data),
};
