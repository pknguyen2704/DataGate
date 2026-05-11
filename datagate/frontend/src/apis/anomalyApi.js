import api from "./api";

export const anomalyApi = {
  aucResults: () => api.get("/anomaly/auc-results"),
  aucResult: (id) => api.get(`/anomaly/auc-results/${id}`),
  aucTimeline: (tableId) => api.get(`/anomaly/tables/${tableId}/auc-timeline`),
  shap: (id) => api.get(`/anomaly/auc-results/${id}/shap`),
  verifyResults: () => api.get("/anomaly/verify-results"),
  resolve: (id) => api.patch(`/anomaly/verify-results/${id}/resolve`),
  unresolve: (id) => api.patch(`/anomaly/verify-results/${id}/unresolve`),
};
