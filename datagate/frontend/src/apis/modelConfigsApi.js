import api from "./api";

const BASE_URL = "/settings/model-configs";

export const modelParametersApi = {
  // Settings CRUD
  list: () => api.get(BASE_URL),
  get: (id) => api.get(`${BASE_URL}/${id}`),
  create: (data) => api.post(BASE_URL, data),
  update: (id, data) => api.patch(`${BASE_URL}/${id}`, data),
  delete: (id) => api.delete(`${BASE_URL}/${id}`),
  
  // Advanced Features
  getTemplate: () => api.get(`${BASE_URL}/template`),
  uploadJson: (tableId, data) => api.post(`${BASE_URL}/upload-json`, data, { params: { table_id: tableId } }),

  // Observability
  aucTimeline: (tableId) => api.get(`${BASE_URL}/auc-results`, { params: { table_id: tableId } }),
  shap: (aucResultId) => api.get(`${BASE_URL}/auc-results/${aucResultId}/shap`),
  tableParameters: (tableId) => api.get(`${BASE_URL}`, { params: { table_id: tableId } }),
};
