import React, { useState } from "react";
import {
  Box,
  Typography,
  TextField,
  Button,
  FormControlLabel,
  Checkbox,
  Link,
  IconButton,
  InputAdornment,
  CircularProgress,
  Alert,
} from "@mui/material";
import { Visibility, VisibilityOff, LockOutlined } from "@mui/icons-material";
import { useNavigate } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import { login } from "~/stores/slices/authSlice";
import { toast } from "react-toastify";
import LogoImage from "~/assets/images/datagate.svg";

const Login = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [formData, setFormData] = useState({
    username: "",
    password: "",
    rememberMe: false,
  });
  const [loginError, setLoginError] = useState("");

  const dispatch = useDispatch();
  const { loading } = useSelector((state) => state.auth);
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value, checked, type } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoginError("");
    try {
      await dispatch(login({ 
        username: formData.username, 
        password: formData.password,
        remember_me: formData.rememberMe 
      })).unwrap();
      toast.success("Welcome back to DataGate!");
      navigate("/app/home");
    } catch (err) {
      const errorMsg = typeof err === 'string' ? err : err?.detail || err?.message || "Invalid credentials. Please try again.";
      setLoginError(errorMsg);
      toast.error(errorMsg);
    }
  };

  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: `linear-gradient(135deg, #F8FAFC 0%, #EFF6FF 100%)`,
        p: 2
      }}
    >
      <Box
        sx={{
          width: "100%",
          maxWidth: 420,
          p: { xs: 4, sm: 5 },
          borderRadius: "16px",
          bgcolor: "#FFFFFF",
          boxShadow: "0 20px 50px rgba(0, 0, 0, 0.05)",
          border: "1px solid rgba(0, 0, 0, 0.05)",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
        }}
      >
        <Box sx={{ mb: 4, display: "flex", flexDirection: "column", alignItems: "center", gap: 1.5 }}>
          <Box 
            sx={{ 
              width: 60, 
              height: 60, 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center', 
              bgcolor: 'primary.main', 
              borderRadius: '12px',
              mb: 1,
              boxShadow: "0 8px 16px rgba(37, 99, 235, 0.2)"
            }}
          >
            <Box component="img" src={LogoImage} alt="DataGate Logo" sx={{ height: 32, filter: 'brightness(0) invert(1)' }} />
          </Box>
          <Typography
            variant="h4"
            sx={{ fontWeight: 800, color: "#0F172A", letterSpacing: "-1px" }}
          >
            DataGate
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>
            Sign in to your account to continue
          </Typography>
        </Box>

        <Box
          component="form"
          onSubmit={handleSubmit}
          sx={{ width: "100%", display: "flex", flexDirection: "column", gap: 2.5 }}
        >
          {loginError && (
            <Alert severity="error" sx={{ borderRadius: 2, '& .MuiAlert-message': { fontWeight: 500 } }}>
              {loginError}
            </Alert>
          )}

          <TextField
            fullWidth
            label="Username or Email"
            name="username"
            type="text"
            variant="outlined"
            required
            autoComplete="username"
            autoFocus
            value={formData.username}
            onChange={handleChange}
            InputProps={{
                sx: { borderRadius: "10px" },
            }}
          />

          <TextField
            fullWidth
            label="Password"
            name="password"
            type={showPassword ? "text" : "password"}
            variant="outlined"
            required
            autoComplete="current-password"
            value={formData.password}
            onChange={handleChange}
            InputProps={{
              sx: { borderRadius: "10px" },
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton
                    onClick={() => setShowPassword((s) => !s)}
                    edge="end"
                    size="small"
                    tabIndex={-1}
                  >
                    {showPassword ? <VisibilityOff fontSize="small" /> : <Visibility fontSize="small" />}
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />

          <Box
            sx={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              mt: -1
            }}
          >
            <FormControlLabel
              control={
                <Checkbox
                  name="rememberMe"
                  size="small"
                  color="primary"
                  checked={formData.rememberMe}
                  onChange={handleChange}
                />
              }
              label={<Typography variant="body2" sx={{ fontWeight: 500 }}>Remember me</Typography>}
            />

          </Box>

          <Button
            fullWidth
            type="submit"
            variant="contained"
            disabled={loading}
            size="large"
            sx={{
              py: 1.6,
              borderRadius: "10px",
              fontWeight: 700,
              fontSize: "1rem",
              textTransform: "none",
              bgcolor: "primary.main",
              boxShadow: "0 10px 20px rgba(37, 99, 235, 0.2)",
              "&:hover": {
                bgcolor: "primary.dark",
                boxShadow: "0 12px 24px rgba(37, 99, 235, 0.3)",
              },
              transition: "all 0.3s ease",
            }}
            startIcon={
              loading ? (
                <CircularProgress size={20} color="inherit" />
              ) : (
                <LockOutlined fontSize="small" />
              )
            }
          >
            {loading ? "Authenticating…" : "Sign In"}
          </Button>
        </Box>

        <Typography
          variant="caption"
          color="text.disabled"
          sx={{ mt: 4, textAlign: "center", fontWeight: 500 }}
        >
          &copy; 2026 DataGate Platform. All rights reserved.
        </Typography>
      </Box>
    </Box>
  );
};

export default Login;
