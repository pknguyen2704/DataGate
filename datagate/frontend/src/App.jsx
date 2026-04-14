import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { Box, Typography, GlobalStyles } from "@mui/material";
import Observability from "~/pages/Observability/Observability";
import Auth from "~/pages/Auth/Auth";
import Login from "~/pages/Auth/Login/Login";
import Home from "~/pages/Home/Home";
import Rules from "~/pages/Rules/Rules";
import AnomalyDetection from "~/pages/AnomalyDetection/AnomalyDetection";
import NotFound from "~/pages/NotFound/NotFound";
import MainLayout from "~/components/Layout/MainLayout";
import Settings from "~/pages/Settings/Settings";
import MetricMonitoring from "~/pages/Metrics/MetricMonitoring";
import DataLineage from "~/pages/Lineage/DataLineage";
import DatasetExplorer from "~/pages/Explorer/DatasetExplorer";
import ProtectedRoute from "./components/Auth/ProtectedRoute";

import "react-toastify/dist/ReactToastify.css";

function App() {
  return (
    <>
      <Routes>
        {/* Auth Routes */}
        <Route path="/auth" element={<Auth />}>
          <Route index element={<Navigate to="login" replace />} />
          <Route path="login" element={<Login />} />
        </Route>

        {/* Protected App Routes */}
        <Route element={<ProtectedRoute />}>
          <Route element={<MainLayout />}>
            <Route path="/" element={<Navigate to="/home" replace={true} />} />
            <Route path="/home" element={<Home />} />
            <Route path="/observability/*" element={<Observability />} />
            <Route path="/rules" element={<Rules />} />
            <Route path="/metrics" element={<MetricMonitoring />} />
            <Route path="/anomaly" element={<AnomalyDetection />} />
            <Route path="/lineage" element={<DataLineage />} />
            <Route path="/explorer" element={<DatasetExplorer />} />
            <Route path="/settings/*" element={<Settings />} />
          </Route>
        </Route>

        {/* 404 Case */}
        <Route path="*" element={<NotFound />} />
      </Routes>
    </>
  );
}

export default App;




