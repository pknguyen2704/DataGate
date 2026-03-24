import React from "react";
import { useNavigate, useLocation } from "react-router-dom";
import {
  AppBar as MuiAppBar,
  Toolbar,
  Box,
  Typography,
  Button,
  useTheme,
  TextField,
  InputAdornment,
  Avatar,
  IconButton,
  Tooltip,
} from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";
import NotificationsNoneIcon from "@mui/icons-material/NotificationsNone";
import SettingsOutlinedIcon from "@mui/icons-material/SettingsOutlined";
import LogoImage from "~/assets/images/datagate.svg";

const navItems = [
  { label: "Home", path: "/home" },
  { label: "Data Profiling", path: "/profiling" },
  { label: "Rule Managements", path: "/rules" },
  { label: "Anomaly Detection", path: "/anomaly" },
];

const AppBar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();

  return (
    <MuiAppBar position="fixed" sx={{ zIndex: theme.zIndex.drawer + 1 }}>
      <Toolbar sx={{ height: theme.datagate.appBarHeight, px: { xs: 2, lg: 4 } }}>
        {/* Logo container */}
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            cursor: "pointer",
            mr: 4,
            px: 1,
            transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
            "&:hover": {
              transform: "translateY(-1px)",
              opacity: 0.9,
            },
            "&:active": { transform: "translateY(0)" },
          }}
          onClick={() => navigate("/home")}
        >
          <Box
            component="img"
            src={LogoImage}
            alt="DataGate Logo"
            sx={{
              height: "32px",
              mr: "12px",
              filter: "brightness(0) invert(1)",
              transition: "transform 0.5s ease",
              "&:hover": { transform: "rotate(10deg)" },
            }}
          />
          <Typography
            variant="h6"
            sx={{
              fontWeight: 700,
              letterSpacing: "-0.02em",
              color: "#ffffff",
              display: { xs: "none", md: "block" },
            }}
          >
            DataGate
          </Typography>
        </Box>

        {/* Search Bar - Center left */}
        <Box sx={{ flexGrow: 0, mr: 4, display: { xs: "none", lg: "block" } }}>
          <TextField
            size="small"
            placeholder="Search platform..."
            sx={{
              width: 300,
              "& .MuiOutlinedInput-root": {
                bgcolor: "rgba(255, 255, 255, 0.1)",
                color: "#ffffff",
                borderRadius: 1,
                "& fieldset": { border: "none" },
                "&:hover": { bgcolor: "rgba(255, 255, 255, 0.15)" },
                "&.Mui-focused": { bgcolor: "rgba(255, 255, 255, 0.2)" },
              },
              "& .MuiInputBase-input::placeholder": {
                color: "rgba(255, 255, 255, 0.6)",
                opacity: 1,
              },
            }}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon sx={{ color: "rgba(255, 255, 255, 0.6)", fontSize: 20 }} />
                </InputAdornment>
              ),
            }}
          />
        </Box>

        {/* Navigation Items */}
        <Box sx={{ display: "flex", gap: 0.5, flexGrow: 1 }}>
          {navItems.map((item) => (
            <Button
              key={item.label}
              variant="text"
              onClick={() => navigate(item.path)}
              sx={{
                color:
                  location.pathname === item.path
                    ? "#ffffff"
                    : "rgba(255,255,255,0.7)",
                fontSize: "0.875rem",
                fontWeight: 600,
                px: 1.5,
                py: 0.75,
                position: "relative",
                borderRadius: 0,
                "&::after": {
                  content: '""',
                  position: "absolute",
                  bottom: 0,
                  left: 0,
                  right: 0,
                  width: location.pathname === item.path ? "100%" : "0",
                  height: "3px",
                  bgcolor: "#ffffff",
                  transition: "width 0.3s ease",
                },
                "&:hover": {
                  bgcolor: "rgba(255,255,255,0.08)",
                  color: "#ffffff",
                  "&::after": { width: "100%" },
                },
              }}
            >
              {item.label}
            </Button>
          ))}
        </Box>

        {/* Right side actions */}
        <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
          <Tooltip title="Notifications">
            <IconButton sx={{ color: "rgba(255, 255, 255, 0.8)", "&:hover": { color: "#fff" } }}>
              <NotificationsNoneIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Settings">
            <IconButton sx={{ color: "rgba(255, 255, 255, 0.8)", "&:hover": { color: "#fff" } }}>
              <SettingsOutlinedIcon />
            </IconButton>
          </Tooltip>
          <Box sx={{ ml: 1, display: "flex", alignItems: "center", cursor: "pointer" }}>
            <Avatar
              sx={{
                width: 32,
                height: 32,
                bgcolor: "secondary.main",
                fontSize: "0.875rem",
                fontWeight: 700,
                border: "2px solid rgba(255,255,255,0.2)",
              }}
            >
              AD
            </Avatar>
          </Box>
        </Box>
      </Toolbar>
    </MuiAppBar>
  );
};

export default AppBar;