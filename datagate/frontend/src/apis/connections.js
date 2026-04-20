import apiClient from "./index";

export const connectionsApi = {
  getConnections: () => apiClient.get("/connections"),
  createConnection: (data) => apiClient.post("/connections", data),
  updateConnection: (id, data) => apiClient.put(`/connections/${id}`, data),
  deleteConnection: (id) => apiClient.delete(`/connections/${id}`),
  testConnection: (data) => apiClient.post("/connections/test", data),
  getRawTables: (url, schema) => 
    apiClient.get("/connections/raw/tables", { params: { url, schema } }),
};
