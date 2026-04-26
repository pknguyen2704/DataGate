import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import Auth from "~/pages/Auth/Auth";
import Login from "~/pages/Auth/Login/Login";
import MainLayout from "~/components/Layout/MainLayout";
import ProtectedRoute from "~/components/Auth/ProtectedRoute";
import "react-toastify/dist/ReactToastify.css";
import { useDispatch } from "react-redux";
import { initializeAuth } from "~/stores/slices/authSlice";

// Pages — lazy loaded for performance
const Home = React.lazy(() => import("~/pages/Home/Home"));
const Tables = React.lazy(() => import("~/pages/Tables/Tables"));
const TableDetail = React.lazy(() => import("~/pages/Tables/TableDetail"));

const Rules = React.lazy(() => import("~/pages/Rules/Rules"));
const Alerts = React.lazy(() => import("~/pages/Alerts/Alerts"));
const Jobs = React.lazy(() => import("~/pages/Jobs/Jobs"));
const Settings = React.lazy(() => import("~/pages/Settings/Settings"));
const NotFound = React.lazy(() => import("~/pages/NotFound/NotFound"));

function App() {
  const dispatch = useDispatch();

  React.useEffect(() => {
    dispatch(initializeAuth());
  }, [dispatch]);

  return (
    <React.Suspense fallback={<div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh', background: '#F7F9FC' }}>Loading...</div>}>
      <Routes>
        {/* Auth Routes */}
        <Route path="/auth" element={<Auth />}>
          <Route index element={<Navigate to="login" replace />} />
          <Route path="login" element={<Login />} />
        </Route>

        {/* Protected App Routes */}
        <Route element={<ProtectedRoute />}>
          <Route element={<MainLayout />}>
            <Route path="/" element={<Navigate to="/home" replace />} />
            <Route path="/home" element={<Home />} />
            <Route path="/tables" element={<Tables />} />
            <Route path="/tables/:tableId" element={<TableDetail />} />

            <Route path="/rules" element={<Rules />} />
            <Route path="/alerts" element={<Alerts />} />
            <Route path="/jobs" element={<Jobs />} />
            <Route path="/settings/*" element={<Settings />} />
          </Route>
        </Route>

        {/* 404 */}
        <Route path="*" element={<NotFound />} />
      </Routes>
    </React.Suspense>
  );
}

export default App;
