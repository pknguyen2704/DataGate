import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import Auth from "~/pages/Auth/Auth";
import Login from "~/pages/Auth/Login/Login";
import Home from "~/pages/Home/Home";
import NotFound from "~/pages/NotFound/NotFound";
import MainLayout from "~/components/Layout/MainLayout";
import Settings from "~/pages/Settings/Settings";
import Explore from "~/pages/Explore/Explore";
import ProtectedRoute from "~/components/Auth/ProtectedRoute";
import "react-toastify/dist/ReactToastify.css";
import { useDispatch } from "react-redux";
import { initializeAuth } from "~/stores/slices/authSlice";

function App() {
  const dispatch = useDispatch();

  React.useEffect(() => {
    dispatch(initializeAuth());
  }, [dispatch]);

  return (
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
          <Route path="/explore" element={<Explore />} />
          <Route path="/settings/*" element={<Settings />} />
        </Route>
      </Route>

      {/* 404 Case */}
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}

export default App;

