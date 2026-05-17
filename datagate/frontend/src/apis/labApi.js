import api from "./api";

export const labApi = {
  getNotebookUrl: () => api.get("/lab/notebook"),
};
