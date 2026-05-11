import api from "./api";

export const healthApi = {
  overview: (params) => api.get("/health/overview", { params }),
  timeline: (params) => api.get("/health/timeline", { params }),
  schemas: (params) => api.get("/health/schemas", { params }),
  schema: (name, params) => api.get(`/health/schemas/${name}`, { params }),
  tables: (params) => api.get("/health/tables", { params }),
  table: (id, params) => api.get(`/health/tables/${id}`, { params }),
};
