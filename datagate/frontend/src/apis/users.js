import apiClient from './index';

export const usersApi = {
  getUsers: (skip = 0, limit = 100) => apiClient.get('/users', { params: { skip, limit } }),
  getMe: () => apiClient.get('/users/me'),
  updateMe: (data) => apiClient.put('/users/me', data),
  getUser: (id) => apiClient.get(`/users/${id}`),
  createUser: (data) => apiClient.post('/users', data),
};
