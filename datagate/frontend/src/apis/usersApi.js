import api from "./api";

const BASE_URL = "/settings/users";

export const usersApi = {
  list: (params) => api.get(BASE_URL, { params }),
  create: (data) => api.post(BASE_URL, data),
  get: (id) => api.get(`${BASE_URL}/${id}`),
  update: (id, data) => api.patch(`${BASE_URL}/${id}`, data),
  delete: (id) => api.delete(`${BASE_URL}/${id}`),
};
