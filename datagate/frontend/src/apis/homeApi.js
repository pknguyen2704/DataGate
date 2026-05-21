import api from "./api";

export const homeApi = {
  summary: (params) => api.get("/home/summary", { params }),
  timeline: (params) => api.get("/home/timeline", { params }),
  tableHealths: (params) => api.get("/home/tables", { params }),
};
