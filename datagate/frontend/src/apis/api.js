import axios from "axios";
export { authApi } from "./authApi";
export { usersApi } from "./usersApi";
export { rolesApi } from "./rolesApi";
export { connectionsApi } from "./connectionsApi";
export { dataAssetsApi } from "./dataAssetsApi";
export { rulesApi } from "./rulesApi";
export { homeApi } from "./homeApi";
export { observabilityApi } from "./observabilityApi";
export { metricsApi } from "./metricsApi";
export { dataQualityApi } from "./dataQualityApi";
export { anomalyJobConfigsApi, modelParametersApi } from "./modelConfigsApi";

const getDefaultApiUrl = () => {
  const { protocol, hostname } = window.location;
  return `${protocol}//${hostname}:8000/api/v1`;
};

const API_BASE_URL = import.meta.env.VITE_API_URL || getDefaultApiUrl();
const api = axios.create({ baseURL: API_BASE_URL, timeout: 30000 });

api.defaults.headers.get['Cache-Control'] = 'no-cache, no-store, must-revalidate';
api.defaults.headers.get['Pragma'] = 'no-cache';
api.defaults.headers.get['Expires'] = '0';

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
}, (error) => Promise.reject(error));

api.interceptors.response.use((response) => response, (error) => {
  if (error.response?.data) {
    const data = error.response.data;
    error.message = data.message || data.detail || error.message;
  }
  if (error.response?.status === 401) {
    localStorage.removeItem("token");
    if (window.location.pathname !== "/auth/login") window.location.href = "/auth/login";
  }
  return Promise.reject(error);
});

export default api;
