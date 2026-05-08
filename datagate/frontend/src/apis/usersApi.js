import api from "./api";
export const usersApi = {
  list: (params) => api.get("/users", { params }),
  create: (data) => api.post("/users", data),
  get: (id) => api.get(`/users/${id}`),
  update: (id, data) => api.patch(`/users/${id}`, data),
  activate: (id) => api.patch(`/users/${id}/activate`),
  deactivate: (id) => api.patch(`/users/${id}/deactivate`),
  assignRoles: (id, data) => api.put(`/users/${id}/roles`, data),
  getMe: () => api.get("/users/me"),
  updateMe: (data) => api.patch("/users/me", data),
};
