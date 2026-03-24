import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { Box, Typography, GlobalStyles } from "@mui/material";
import Profiling from "~/pages/Profiling/Profiling";
import Auth from "~/pages/Auth/Auth";
import Login from "~/pages/Auth/Login/Login";
import MainLayout from "~/components/Layout/MainLayout";

function App() {
  return (
    <>
      <GlobalStyles
        styles={{
          "@import": [
            'url("https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;500;600;700&family=Poppins:wght@400;500;600;700&display=swap")',
          ],
          body: {
            margin: 0,
            padding: 0,
            transition: "background-color 0.3s ease",
            fontFamily: '"Open Sans", sans-serif',
          },
        }}
      />
      <Routes>
        {/* Auth Routes */}
        <Route path="/auth" element={<Auth />}>
          <Route index element={<Navigate to="login" replace />} />
          <Route path="login" element={<Login />} />
        </Route>

        {/* Protected App Routes */}
        <Route element={<MainLayout />}>
          <Route path="/" element={<Navigate to="/home" replace={true} />} />
          <Route
            path="/home"
            element={
              <Box
                sx={{
                  textAlign: "center",
                  mt: 10,
                  animation: "fadeIn 1s ease",
                  "@keyframes fadeIn": {
                    from: { opacity: 0, transform: "translateY(10px)" },
                    to: { opacity: 1, transform: "translateY(0)" },
                  },
                }}
              >
                <Typography variant="h2" color="primary.main" gutterBottom>
                  Welcome to DataGate
                </Typography>
                <Typography variant="h6" color="text.secondary">
                  Your modern data governance and anomaly detection platform
                </Typography>
              </Box>
            }
          />
          <Route path="/profiling" element={<Profiling />} />
          <Route
            path="/rules"
            element={
              <Box sx={{ p: 4 }}>
                <h1>Rule Managements Page</h1>
              </Box>
            }
          />
          <Route
            path="/anomaly"
            element={
              <Box sx={{ p: 4 }}>
                <h1>Anomaly Detection Page</h1>
              </Box>
            }
          />
        </Route>

        {/* 404 Case */}
        <Route
          path="*"
          element={
            <Box sx={{ p: 4 }}>
              <h1>404 Not Found</h1>
            </Box>
          }
        />
      </Routes>
    </>
  );
}

export default App;




