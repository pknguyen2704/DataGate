export const getErrorMessage = (error, fallback) =>
  error.response?.data?.detail || error.message || fallback;
