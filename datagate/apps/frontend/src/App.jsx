import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { Box, Typography, GlobalStyles } from "@mui/material";
import Profiling from "~/pages/Profiling/Profiling";
import Auth from "~/pages/Auth/Auth";
import Login from "~/pages/Auth/Login/Login";
import Home from "~/pages/Home/Home";
import Rules from "~/pages/Rules/Rules";
import AnomalyDetection from "~/pages/AnomalyDetection/AnomalyDetection";
import NotFound from "~/pages/NotFound/NotFound";
import MainLayout from "~/components/Layout/MainLayout";
import Settings from "~/pages/Settings/Settings";

import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

function App() {
  return (
    <>
      <ToastContainer position="top-right" autoClose={3000} hideProgressBar={false} />
      <Routes>
        {/* Auth Routes */}
        <Route path="/auth" element={<Auth />}>
          <Route index element={<Navigate to="login" replace />} />
          <Route path="login" element={<Login />} />
        </Route>

        {/* Protected App Routes */}
        <Route element={<MainLayout />}>
          <Route path="/" element={<Navigate to="/home" replace={true} />} />
          <Route path="/home" element={<Home />} />
          <Route path="/profiling/*" element={<Profiling />} />
          <Route path="/rules" element={<Rules />} />
          <Route path="/anomaly" element={<AnomalyDetection />} />
          <Route path="/settings/*" element={<Settings />} />
        </Route>

        {/* 404 Case */}
        <Route path="*" element={<NotFound />} />
      </Routes>
    </>
  );
}

export default App;




