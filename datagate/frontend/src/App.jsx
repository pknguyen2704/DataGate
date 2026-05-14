import React, { useEffect } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import Auth from "~/pages/Auth/Auth";
import Login from "~/pages/Auth/Login/Login";
import MainLayout from "~/components/Layout/MainLayout";
import ProtectedRoute from "~/components/Auth/ProtectedRoute";
import "react-toastify/dist/ReactToastify.css";
import { useDispatch } from "react-redux";
import { initializeAuth } from "~/stores/slices/authSlice";

// Explicit imports replacing React.lazy for simpler, beginner-friendly code
import Home from "~/pages/Home/Home";
import DataAssets from "~/pages/DataAssets/DataAssets";
import TableDetail from "~/pages/DataAssets/TableDetail/index.jsx";
import Settings from "~/pages/Settings/Settings";
import { ObservabilityTab, MetricsTab, RulesTab, QualityTab } from "~/pages/DataAssets/TableDetail/index.jsx";
import PlatformConnection from "~/pages/Settings/PlatformConnection/PlatformConnection";
import ModelParameter from "~/pages/Settings/ModelParameter/ModelParameter";
import UserManagement from "~/pages/Settings/UserManagement/UserManagement";
import RoleManagement from "~/pages/Settings/RoleManagement/RoleManagement";

function App() {
  const dispatch = useDispatch();

  useEffect(() => {
    dispatch(initializeAuth());
  }, [dispatch]);

  return (
    <Routes>
      {/* Auth Routes */}
      <Route path="/login" element={<Login />} />

      {/* Protected App Routes */}
      <Route element={<ProtectedRoute />}>
        <Route element={<MainLayout />}>
          <Route path="/" element={<Navigate to="/app/home" replace />} />
          <Route path="/app/home" element={<Home />} />

          {/* Data Assets */}
          <Route path="/app/data-assets" element={<DataAssets />} />
          <Route path="/app/data-assets/:tableId" element={<TableDetail />}>
            <Route index element={<Navigate to="observability" replace />} />
            <Route path="observability" element={<ObservabilityTab />} />
            <Route path="metrics" element={<MetricsTab />} />
            <Route path="rules" element={<RulesTab />} />
            <Route path="data-quality" element={<QualityTab />} />
          </Route>

          {/* Settings */}
          <Route path="/app/settings" element={<Settings />}>
            <Route index element={<Navigate to="model-configs" replace />} />
            
            <Route element={<ProtectedRoute permission="connection:view" />}>
              <Route path="connections" element={<PlatformConnection />} />
            </Route>

            <Route path="model-configs" element={<ModelParameter />} />
            
            <Route element={<ProtectedRoute permission="user:view" />}>
              <Route path="users" element={<UserManagement />} />
              <Route path="roles" element={<RoleManagement />} />
            </Route>
          </Route>
        </Route>
      </Route>

      {/* 404 */}
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}

export default App;
