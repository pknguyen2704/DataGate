import api from "./api";

const BASE_URL = "/settings/roles";

export const rolesApi = {
  list: () => api.get(BASE_URL),
  get: (id) => api.get(`${BASE_URL}/${id}`),
};
