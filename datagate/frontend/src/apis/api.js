export { authApi } from "./authApi";
export { usersApi } from "./usersApi";
export { rolesApi } from "./rolesApi";
export { connectionsApi } from "./connectionsApi";
export { tablesApi } from "./tablesApi";
export { rulesApi } from "./rulesApi";
export { exploreApi } from "./exploreApi";

import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_URL || `http://localhost:8000/api/v1`;

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("token");

      if (window.location.pathname !== "/auth/login") {
        window.location.href = "/auth/login";
      }
    }

    return Promise.reject(error);
  }
);

export default api;