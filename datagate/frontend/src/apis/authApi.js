import api from "./api";

export const authApi = {
  login: (data) =>
    api.post("/auth/login", data),

  getMe: () => api.get("/auth/me"),

  changePassword: (data) => api.post("/auth/me/password", data),

  logout: () => api.post("/auth/logout"),
};
