import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import Auth from "~/pages/Auth/Auth";
import Login from "~/pages/Auth/Login/Login";
import MainLayout from "~/components/Layout/MainLayout";
import ProtectedRoute from "~/components/Auth/ProtectedRoute";
import "react-toastify/dist/ReactToastify.css";
import { useDispatch } from "react-redux";
import { initializeAuth } from "~/stores/slices/authSlice/authSlice";

// Pages — lazy loaded for performance
const Home = React.lazy(() => import("~/pages/Home/Home"));
const Explore = React.lazy(() => import("~/pages/Explore/Explore"));

const Settings = React.lazy(() => import("~/pages/Settings/Settings"));
const NotFound = React.lazy(() => import("~/pages/NotFound/NotFound"));

function App() {
  const dispatch = useDispatch();

  React.useEffect(() => {
    dispatch(initializeAuth());
  }, [dispatch]);

  return (
    <React.Suspense fallback={<div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh', background: '#F8FAFC', color: '#0F172A' }}>Loading...</div>}>
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
            <Route path="/explore/*" element={<Explore />} />
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
