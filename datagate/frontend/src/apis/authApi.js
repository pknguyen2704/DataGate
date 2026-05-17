import api from "./api";

export const authApi = {
  login: (data) =>
    api.post("/auth/login", data),

  getMe: () => api.get("/auth/me"),

  logout: () => api.post("/auth/logout"),
};
