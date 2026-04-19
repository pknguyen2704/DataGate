import React from "react";
import {
  Box,
  Typography,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Tooltip,
} from "@mui/material";
import {
  DashboardOutlined as DashboardIcon,
  SearchOutlined as ExplorerIcon,
  QueryStatsOutlined as MetricsIcon,
  SettingsOutlined as SettingsIcon,
} from "@mui/icons-material";
import { useTheme } from "@mui/material/styles";
import { useNavigate, useLocation } from "react-router-dom";
import DataGateLogo from "~/assets/images/datagate.svg";

const navItems = [
  { text: "Home", icon: <DashboardIcon />, path: "/home" },
  { text: "Explore", icon: <ExplorerIcon />, path: "/explore" },
  { text: "Settings", icon: <SettingsIcon />, path: "/settings" },
];

const SideBar = ({ isCollapsed }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();

  const isActive = (path) => {
    if (path === "/home") {
      return location.pathname === "/home";
    }
    return location.pathname.startsWith(path);
  };

  return (
    <Box
      sx={{
        width: isCollapsed ? "80px" : theme.datagate.sidebarWidth,
        minWidth: isCollapsed ? "80px" : theme.datagate.sidebarWidth,
        flexShrink: 0,
        height: "100%",
        display: "flex",
        flexDirection: "column",
        bgcolor: "background.default",
        transition: "width 0.3s cubic-bezier(0.4, 0, 0.2, 1), min-width 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
        overflowX: "hidden",
        zIndex: 1200,
        boxShadow: 'none',
        border: 'none',
      }}
    >
      <Box
        sx={{
          px: isCollapsed ? 0 : 2,
          py: 2.5,
          display: "flex",
          alignItems: "center",
          justifyContent: isCollapsed ? "center" : "flex-start",
          minHeight: "80px",
          gap: 1.5,
        }}
      >
        <Box
          component="img"
          src={DataGateLogo}
          alt="DataGate Logo"
          sx={{ width: 32, height: 32, objectFit: "contain", flexShrink: 0 }}
        />
        {!isCollapsed && (
          <Typography
            variant="h6"
            sx={{ fontWeight: 800, color: "primary.main", letterSpacing: "-0.5px", whiteSpace: "nowrap" }}
          >
            DataGate
          </Typography>
        )}
      </Box>

      <List sx={{ flexGrow: 1, px: 0 }}>
        {navItems.map((item) => (
          <Tooltip key={item.text} title={isCollapsed ? item.text : ""} placement="right">
            <ListItemButton
              selected={isActive(item.path)}
              onClick={() => navigate(item.path)}
              sx={{
                mx: 1,
                mb: 0.5,
                borderRadius: 1,
                justifyContent: isCollapsed ? "center" : "flex-start",
                px: isCollapsed ? 0 : 2,
                minHeight: 44,
                "&.Mui-selected": {
                  bgcolor: "primary.50",
                  color: "primary.main",
                  "&:hover": { bgcolor: "primary.50" },
                },
              }}
            >
              <ListItemIcon
                sx={{
                  minWidth: isCollapsed ? 0 : 40,
                  display: "flex",
                  justifyContent: "center",
                  color: isActive(item.path) ? "primary.main" : "text.secondary",
                }}
              >
                {item.icon}
              </ListItemIcon>
              {!isCollapsed && (
                <ListItemText 
                  primary={item.text} 
                  slotProps={{
                    primary: {
                      fontSize: "0.875rem",
                      fontWeight: isActive(item.path) ? 700 : 500,
                    },
                  }}
                />
              )}
            </ListItemButton>
          </Tooltip>
        ))}
      </List>
    </Box>
  );
};

export default SideBar;
