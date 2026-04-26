import apiClient from './index';

export const authApi = {
  login: (username, password) =>
    apiClient.post('/auth/login', { username, password }),

  getMe: () => apiClient.get('/auth/me'),

  logout: () => apiClient.post('/auth/logout'),
};
