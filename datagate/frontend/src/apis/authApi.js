import api from "./api";

export const authApi = {
  login: (username, password) =>
    api.post("/auth/login", { username, password }),

  getMe: () => api.get("/auth/me"),

  changePassword: (data) => api.post("/auth/me/password", data),

  logout: () => api.post("/auth/logout"),
};
