import apiClient from './index';

export const authApi = {
  login: async (email, password) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    
    return apiClient.post(`/auth/login/access-token`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  
  getMe: async () => {
    return apiClient.get(`/auth/me`);
  },
};
