import React, { useEffect } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { useDispatch } from "react-redux";
import { initializeAuth } from "~/stores/slices/authSlice";
import "react-toastify/dist/ReactToastify.css";
import ProtectedRoute from "~/components/Auth/ProtectedRoute";
import MainLayout from "~/components/Layout/MainLayout";
import Auth from "~/pages/Auth/Auth";
import Home from "~/pages/Home/Home";
import DataAssets from "~/pages/DataAssets/DataAssets";
import Analysis from "~/pages/Analysis/Analysis";
import TableDetail, {
  ObservabilityTab,
  MetricsTab,
  RulesTab,
  QualityTab,
} from "~/pages/DataAssets/TableDetail/index.jsx";
import Settings from "~/pages/Settings/Settings";
import PlatformConnection from "~/pages/Settings/PlatformConnection/PlatformConnection";
import AnomalyConfig from "~/pages/Settings/AnomalyConfig/AnomalyConfig";
import UserManagement from "~/pages/Settings/UserManagement/UserManagement";

import { PermissionCode } from "~/rbac/permission";

function App() {
  const dispatch = useDispatch();

  useEffect(() => {
    dispatch(initializeAuth());
  }, [dispatch]);

  return (
    <Routes>
      {/* Public route */}
      <Route path="/login" element={<Auth />} />

      {/* Protected app */}
      <Route element={<ProtectedRoute />}>
        <Route element={<MainLayout />}>
          <Route path="/" element={<Navigate to="/app/home" replace />} />

          <Route
            path="/app/home"
            element={
              <ProtectedRoute permission={PermissionCode.HOME_VIEW}>
                <Home />
              </ProtectedRoute>
            }
          />

          <Route
            path="/app/analysis"
            element={
              <ProtectedRoute permission={PermissionCode.LAB_VIEW}>
                <Analysis />
              </ProtectedRoute>
            }
          />

          {/* Data Assets */}
          <Route
            path="/app/data-assets"
            element={
              <ProtectedRoute permission={PermissionCode.OBSERVABILITY_VIEW}>
                <DataAssets />
              </ProtectedRoute>
            }
          />

          <Route path="/app/data-assets/:tableId" element={<TableDetail />}>
            <Route index element={<Navigate to="observability" replace />} />

            <Route
              path="observability"
              element={
                <ProtectedRoute permission={PermissionCode.OBSERVABILITY_VIEW}>
                  <ObservabilityTab />
                </ProtectedRoute>
              }
            />

            <Route
              path="metrics"
              element={
                <ProtectedRoute permission={PermissionCode.THRESHOLD_MANAGE}>
                  <MetricsTab />
                </ProtectedRoute>
              }
            />

            <Route
              path="rules"
              element={
                <ProtectedRoute permission={PermissionCode.RULE_MANAGE}>
                  <RulesTab />
                </ProtectedRoute>
              }
            />

            <Route
              path="data-quality"
              element={
                <ProtectedRoute permission={PermissionCode.QUALITY_VIEW}>
                  <QualityTab />
                </ProtectedRoute>
              }
            />
          </Route>

          {/* Settings */}
          <Route path="/app/settings" element={<Settings />}>
            <Route index element={null} />

            <Route
              path="connections"
              element={
                <ProtectedRoute permission={PermissionCode.CONNECTION_MANAGE}>
                  <PlatformConnection />
                </ProtectedRoute>
              }
            />

            <Route
              path="anomaly-configs"
              element={
                <ProtectedRoute permission={PermissionCode.ANOMALY_CONFIG_MANAGE}>
                  <AnomalyConfig />
                </ProtectedRoute>
              }
            />

            <Route
              path="users"
              element={
                <ProtectedRoute permission={PermissionCode.USER_MANAGE}>
                  <UserManagement />
                </ProtectedRoute>
              }
            />
          </Route>
        </Route>
      </Route>

      {/* 404 */}
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}

export default App;