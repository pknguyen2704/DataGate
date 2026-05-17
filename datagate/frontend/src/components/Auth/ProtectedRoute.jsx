import { useSelector } from 'react-redux'
import { Box, CircularProgress } from '@mui/material'
import { Navigate, Outlet, useLocation } from 'react-router-dom'

const ProtectedRoute = ({ permission }) => {
  const { isAuthenticated, loading, user } = useSelector((state) => state.auth)
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

  // Permission check
  if (permission && !user?.permissions?.includes(permission)) {
    return <Navigate to="/app/home" replace />;
  }

  return <Outlet />
};

export default ProtectedRoute;