import api from "./api";

export const homeApi = {
  overview: (params) => api.get("/home/overview", { params }),
  summary: (params) => api.get("/home/summary", { params }),
  timeline: (params) => api.get("/home/timeline", { params }),
  tableHealths: (params) => api.get("/home/tables", { params }),
  tableHealth: (id, params) => api.get(`/home/tables/${id}`, { params }),
};
