// API clients for all modules
import apiClient from './index';

// ── Auth ──────────────────────────────────────────────────────────────────────
export const authApi = {
  login: (username, password) =>
    apiClient.post('/auth/login', { username, password }),
  getMe: () => apiClient.get('/auth/me'),
  logout: () => apiClient.post('/auth/logout'),
};

// ── Users ─────────────────────────────────────────────────────────────────────
export const usersApi = {
  list: (params) => apiClient.get('/users', { params }),
  create: (data) => apiClient.post('/users', data),
  get: (id) => apiClient.get(`/users/${id}`),
  update: (id, data) => apiClient.patch(`/users/${id}`, data),
  deactivate: (id) => apiClient.delete(`/users/${id}`),
  assignRoles: (id, roleIds) => apiClient.post(`/users/${id}/roles`, roleIds),
};

// ── Roles & Permissions ───────────────────────────────────────────────────────
export const rolesApi = {
  list: () => apiClient.get('/roles'),
  create: (data) => apiClient.post('/roles', data),
  get: (id) => apiClient.get(`/roles/${id}`),
  update: (id, data) => apiClient.patch(`/roles/${id}`, data),
  delete: (id) => apiClient.delete(`/roles/${id}`),
  assignPermissions: (id, permIds) => apiClient.post(`/roles/${id}/permissions`, permIds),
  listPermissions: () => apiClient.get('/roles/permissions'),
};

// ── Connections ───────────────────────────────────────────────────────────────
export const connectionsApi = {
  list: () => apiClient.get('/connections'),
  create: (data) => apiClient.post('/connections', data),
  get: (id) => apiClient.get(`/connections/${id}`),
  update: (id, data) => apiClient.patch(`/connections/${id}`, data),
  delete: (id) => apiClient.delete(`/connections/${id}`),
  test: (id) => apiClient.post(`/connections/${id}/test`),
};

// ── Tables ────────────────────────────────────────────────────────────────────
export const tablesApi = {
  list: (params) => apiClient.get('/tables', { params }),
  create: (data) => apiClient.post('/tables', data),
  get: (id) => apiClient.get(`/tables/${id}`),
  update: (id, data) => apiClient.patch(`/tables/${id}`, data),
  grantAccess: (id, data) => apiClient.post(`/tables/${id}/access`, data),
  revokeAccess: (id, userId) => apiClient.delete(`/tables/${id}/access/${userId}`),

  // Sub-resources
  getMetadata: (id, params) => apiClient.get(`/tables/${id}/metadata`, { params }),
  getProfiling: (id, params) => apiClient.get(`/tables/${id}/profiling`, { params }),
  getRules: (id, params) => apiClient.get(`/tables/${id}/rules`, { params }),
  getQuality: (id, params) => apiClient.get(`/tables/${id}/quality`, { params }),
  getAnomaly: (id, params) => apiClient.get(`/tables/${id}/anomaly`, { params }),
  getThresholds: (id) => apiClient.get(`/tables/${id}/thresholds`),
  getAlerts: (id, params) => apiClient.get(`/tables/${id}/alerts`, { params }),
  getJobs: (id, params) => apiClient.get(`/tables/${id}/jobs`, { params }),
};

// ── Rules ─────────────────────────────────────────────────────────────────────
export const rulesApi = {
  list: (params) => apiClient.get('/rules', { params }),
  create: (data) => apiClient.post('/rules', data),
  update: (id, data) => apiClient.patch(`/rules/${id}`, data),
  updateStatus: (id, status) => apiClient.patch(`/rules/${id}/status`, { status }),
  delete: (id) => apiClient.delete(`/rules/${id}`),
};

// ── Alerts ────────────────────────────────────────────────────────────────────
export const alertsApi = {
  list: (params) => apiClient.get('/alerts', { params }),
  updateStatus: (id, status, note) => apiClient.patch(`/alerts/${id}/status`, { status, note }),
};

// ── Jobs ──────────────────────────────────────────────────────────────────────
export const jobsApi = {
  list: (params) => apiClient.get('/jobs', { params }),
  trigger: (data) => apiClient.post('/jobs/trigger', data),
};

// ── Thresholds ────────────────────────────────────────────────────────────────
export const thresholdsApi = {
  list: (params) => apiClient.get('/thresholds', { params }),
  create: (data) => apiClient.post('/thresholds', data),
  update: (id, data) => apiClient.patch(`/thresholds/${id}`, data),
  delete: (id) => apiClient.delete(`/thresholds/${id}`),
};

// ── Dashboard ─────────────────────────────────────────────────────────────────
export const dashboardApi = {
  getSummary: () => apiClient.get('/dashboard/summary'),
};
