import React, { useState } from "react";
import {
  Box,
  Typography,
  TextField,
  Button,
  Checkbox,
  FormControlLabel,
  Link,
  IconButton,
  InputAdornment,
  Divider,
} from "@mui/material";
import { Visibility, VisibilityOff, GitHub, Google } from "@mui/icons-material";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../../contexts/AuthContext";
import { toast } from "react-toastify";
import LogoImage from "../../../assets/images/datagate.svg";

const Login = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    rememberMe: false,
  });

  const { login } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const handleClickShowPassword = () => setShowPassword((show) => !show);

  const handleChange = (e) => {
    const { name, value, checked, type } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await login(formData.email, formData.password);
      toast.success("Welcome back to DataGate!");
      navigate("/");
    } catch (err) {
      const errorMsg = err.response?.data?.detail || "Invalid credentials. Please try again.";
      toast.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        width: "100%",
        p: 4,
        borderRadius: 1, // Strictly 1 as per theme.js
        bgcolor: "rgba(255, 255, 255, 0.8)",
        backdropFilter: "blur(20px)",
        boxShadow: "0 8px 32px 0 rgba(31, 38, 135, 0.2)",
        border: "1px solid rgba(255, 255, 255, 0.18)",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        animation: "slideUp 0.6s ease-out",
        "@keyframes slideUp": {
          from: { opacity: 0, transform: "translateY(30px)" },
          to: { opacity: 1, transform: "translateY(0)" },
        },
      }}
    >
      {/* Logo and Header */}
      <Box
        sx={{
          mb: 4,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
        }}
      >
        <Box
          component="img"
          src={LogoImage}
          alt="DataGate Logo"
          sx={{ height: 48, mb: 1.5 }}
        />
        <Typography
          variant="h4"
          sx={{
            fontWeight: 700,
            color: "primary.main",
            mb: 0.5,
          }}
        >
          Welcome Back
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Manage your data with confidence
        </Typography>
      </Box>

      {/* Login Form */}
      <Box
        component="form"
        onSubmit={handleSubmit}
        sx={{ width: "100%", mb: 3 }}
      >
        <TextField
          fullWidth
          label="Email Address"
          name="email"
          type="email"
          variant="outlined"
          margin="normal"
          required
          value={formData.email}
          onChange={handleChange}
          sx={{
            "& .MuiOutlinedInput-root": {
              borderRadius: 1,
            },
          }}
        />
        <TextField
          fullWidth
          label="Password"
          name="password"
          type={showPassword ? "text" : "password"}
          variant="outlined"
          margin="normal"
          required
          value={formData.password}
          onChange={handleChange}
          sx={{
            "& .MuiOutlinedInput-root": {
              borderRadius: 1,
            },
          }}
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                <IconButton onClick={handleClickShowPassword} edge="end">
                  {showPassword ? <VisibilityOff /> : <Visibility />}
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
            mt: 1,
            mb: 2,
          }}
        >
          <FormControlLabel
            control={
              <Checkbox
                name="rememberMe"
                color="primary"
                checked={formData.rememberMe}
                onChange={handleChange}
                size="small"
              />
            }
            label={
              <Typography variant="body2" sx={{ fontSize: "0.875rem" }}>
                Remember me
              </Typography>
            }
          />
          <Link
            href="#"
            variant="body2"
            sx={{
              fontWeight: 600,
              textDecoration: "none",
              color: "primary.main",
              "&:hover": { textDecoration: "underline" },
            }}
          >
            Forgot password?
          </Link>
        </Box>

        <Button
          fullWidth
          type="submit"
          variant="contained"
          disabled={loading}
          sx={{
            py: 1.5,
            fontSize: "1rem",
            fontWeight: 700,
            bgcolor: "secondary.main", // Accent green as per theme.js/design-system
            "&:hover": {
              bgcolor: "secondary.dark",
            },
            borderRadius: 1,
            textTransform: "none"
          }}
        >
          {loading ? "Authenticating..." : "Sign In"}
        </Button>
      </Box>

      <Divider sx={{ width: "100%", mb: 3 }}>
        <Typography variant="body2" color="text.secondary">
          OR CONTINUE WITH
        </Typography>
      </Divider>

      {/* Social Login */}
      <Box sx={{ display: "flex", gap: 2, width: "100%", mb: 4 }}>
        <Button
          fullWidth
          variant="outlined"
          startIcon={<Google />}
          sx={{
            borderRadius: 1,
            color: "text.primary",
            borderColor: "divider",
            py: 1,
            "&:hover": {
              borderColor: "primary.main",
              bgcolor: "transparent",
            },
          }}
        >
          Google
        </Button>
        <Button
          fullWidth
          variant="outlined"
          startIcon={<GitHub />}
          sx={{
            borderRadius: 1,
            color: "text.primary",
            borderColor: "divider",
            py: 1,
            "&:hover": {
              borderColor: "primary.main",
              bgcolor: "transparent",
            },
          }}
        >
          GitHub
        </Button>
      </Box>

      <Typography variant="body2" color="text.secondary">
        Don't have an account?{" "}
        <Link
          href="#"
          sx={{
            fontWeight: 700,
            textDecoration: "none",
            color: "primary.main",
            "&:hover": { textDecoration: "underline" },
          }}
        >
          Create an account
        </Link>
      </Typography>
    </Box>
  );
};

export default Login;