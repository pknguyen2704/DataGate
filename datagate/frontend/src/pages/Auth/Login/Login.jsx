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
} from "@mui/material";
import { Visibility, VisibilityOff, LockOutlined } from "@mui/icons-material";
import { useNavigate } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import { login } from "~/stores/slices/authSlice/authSlice";
import { toast } from "react-toastify";
import LogoImage from "~/assets/images/datagate.svg";

const Login = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [formData, setFormData] = useState({
    username: "",
    password: "",
    rememberMe: false,
  });

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
    try {
      await dispatch(login({ username: formData.username, password: formData.password })).unwrap();
      toast.success("Welcome back to DataGate!");
      navigate("/");
    } catch (err) {
      toast.error(err || "Invalid credentials. Please try again.");
    }
  };

  return (
    <Box
      sx={{
        width: "100%",
        maxWidth: 420,
        p: { xs: 3, sm: 4.5 },
        borderRadius: "16px",
        bgcolor: "#FFFFFF",
        backdropFilter: "blur(24px)",
        boxShadow: "0 18px 48px rgba(15, 23, 42, 0.12)",
        border: "1px solid #E2E8F0",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        animation: "slideUp 0.5s cubic-bezier(0.22, 1, 0.36, 1)",
        "@keyframes slideUp": {
          from: { opacity: 0, transform: "translateY(24px)" },
          to: { opacity: 1, transform: "translateY(0)" },
        },
      }}
    >
      <Box sx={{ mb: 3, display: "flex", flexDirection: "column", alignItems: "center", gap: 1 }}>
        <Box component="img" src={LogoImage} alt="DataGate Logo" sx={{ height: 48 }} />
        <Typography
          variant="h5"
          sx={{ fontWeight: 700, color: "primary.main", letterSpacing: "-0.5px" }}
        >
          Sign in to DataGate
        </Typography>
      </Box>

      <Box
        component="form"
        onSubmit={handleSubmit}
        sx={{ width: "100%", display: "flex", flexDirection: "column", gap: 2 }}
      >
        <TextField
          fullWidth
          label="Username"
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
            label={<Typography variant="body2">Remember me</Typography>}
          />
          <Link
            href="#"
            variant="body2"
            underline="hover"
            sx={{ fontWeight: 600, color: "primary.main" }}
          >
            Forgot password?
          </Link>
        </Box>

        <Button
          fullWidth
          type="submit"
          variant="contained"
          disabled={loading}
          size="large"
          sx={{
            mt: 0.5,
            py: 1.4,
            borderRadius: "10px",
            fontWeight: 700,
            fontSize: "0.95rem",
            textTransform: "none",
            bgcolor: "primary.main",
            boxShadow: "0 4px 14px rgba(37,99,235,0.35)",
            "&:hover": {
              bgcolor: "primary.dark",
              boxShadow: "0 6px 20px rgba(37,99,235,0.45)",
            },
            transition: "all 0.2s ease",
          }}
          startIcon={
            loading ? (
              <CircularProgress size={18} color="inherit" />
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
        sx={{ mt: 3, textAlign: "center" }}
      >
        Access is restricted to authorized personnel only.
      </Typography>
    </Box>
  );
};

export default Login;
