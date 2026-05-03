import api from "./api";

export const authApi = {
  login: (username, password) =>
    api.post('/auth/login', { username, password }),

  getMe: () => api.get('/auth/me'),

  logout: () => api.post('/auth/logout'),
};