import { Box, CircularProgress } from '@mui/material'
import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useRBAC } from '~/rbac/useRBAC'

const ProtectedRoute = ({ permission, children }) => {
  const { isAuthenticated, loading, hasPermission } = useRBAC();
  const location = useLocation();

  if (loading) {
    return (
      <Box
        sx={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          height: "100vh",
        }}
      >
        <CircularProgress />
      </Box>
    )
  }

  if (!isAuthenticated) {
    return (
      <Navigate
        to="/login"
        state={{ from: location }}
        replace
      />
    )
  }

  if (permission && !hasPermission(permission)) {
    return <Navigate to="/app/home" replace />;
  }

  return children ? children : <Outlet />;
};

export default ProtectedRoute;