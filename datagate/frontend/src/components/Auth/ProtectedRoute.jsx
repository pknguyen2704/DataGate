import React from 'react'
import { useSelector } from 'react-redux'
import { Box, CircularProgress } from '@mui/material'
import { Navigate, Outlet, useLocation } from 'react-router-dom'

const ProtectedRoute = () => {
  const { isAuthenticated, loading } = useSelector((state) => state.auth)
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
        to="/auth/login"
        state={{ from: location }}
        replace
      />
    )
  }

  return <Outlet />
};

export default ProtectedRoute;