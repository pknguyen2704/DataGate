import api from "./api";

export const permissionsApi = {
  list: () => api.get("/permissions"),
  listGrouped: () => api.get("/permissions/grouped"),
};
