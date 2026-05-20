import api from "./api";

export const labApi = {
  getAnalysisUrl: () => api.get("/lab/analysis"),
};
