import React from "react";
import {
  Box,
  Divider,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Tooltip,
  Typography,
} from "@mui/material";
import {
  DashboardOutlined as DashboardIcon,
  MenuBookOutlined as NotebookIcon,
  SettingsOutlined as SettingsIcon,
  TableChartOutlined as TablesIcon,
} from "@mui/icons-material";
import { useTheme } from "@mui/material/styles";
import { useNavigate, useLocation } from "react-router-dom";
import { useSelector } from "react-redux";
import DataGateLogo from "~/assets/images/datagate.svg";
import { datagateColors } from "~/theme";

const getNavItems = () => [
  {
    text: "Home",
    icon: <DashboardIcon />,
    path: "/app/home",
    permission: "home:view",
  },
  {
    text: "Data Assets",
    icon: <TablesIcon />,
    path: "/app/data-assets",
    permission: "table:view",
  },
  {
    text: "Notebook",
    icon: <NotebookIcon />,
    path: "/app/notebook",
    permission: "lab:view",
  },
];

const SideBar = ({ isCollapsed }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const { user } = useSelector((state) => state.auth);
  const permissions = user?.permissions || [];

  const navItems = getNavItems();

  const hasPermission = (permCode) => {
    if (!permCode) return true;
    return permissions.includes(permCode);
  };

  const isActive = (path) => {
    if (path === "/home") return location.pathname === "/home";
    return location.pathname.startsWith(path);
  };

  const visibleItems = navItems.filter((item) => hasPermission(item.permission));

  return (
      <Box
        sx={{
          width: isCollapsed ? "72px" : theme.datagate.sidebarWidth,
        minWidth: isCollapsed ? "72px" : theme.datagate.sidebarWidth,
        flexShrink: 0,
        height: "100%",
        display: "flex",
        flexDirection: "column",
        bgcolor: "transparent",
        transition: "width 0.25s cubic-bezier(0.4,0,0.2,1), min-width 0.25s cubic-bezier(0.4,0,0.2,1)",
          overflowX: "hidden",
          borderRight: `1px solid ${datagateColors.shellLine}`,
          background: `linear-gradient(180deg, ${datagateColors.shell} 0%, ${datagateColors.shellSoft} 100%)`,
        }}
    >
      {/* Logo */}
      <Box
        sx={{
          px: isCollapsed ? 0 : 2.5,
          py: 2.5,
          display: "flex",
          alignItems: "center",
          justifyContent: isCollapsed ? "center" : "flex-start",
          minHeight: "72px",
          gap: 1.5,
        }}
      >
        <Box
          component="img"
          src={DataGateLogo}
          alt="DataGate"
          sx={{ width: 28, height: 28, objectFit: "contain", flexShrink: 0 }}
        />
        {!isCollapsed && (
          <Typography
            variant="h6"
            sx={{
              fontWeight: 800,
              color: "#FFFFFF",
              letterSpacing: "-0.5px",
              whiteSpace: "nowrap",
              fontSize: "1.05rem",
            }}
          >
            DataGate
          </Typography>
        )}
      </Box>

      <Divider />

      {/* Main nav */}
      <List sx={{ flexGrow: 1, px: 1, pt: 1 }}>
        {visibleItems.map((item) => (
          <Tooltip key={item.text} title={isCollapsed ? item.text : ""} placement="right">
            <ListItemButton
              selected={isActive(item.path)}
              onClick={() => navigate(item.path)}
              sx={{
                mb: 1,
                borderRadius: 0,
                mr: 0,
                justifyContent: isCollapsed ? "center" : "flex-start",
                px: isCollapsed ? 0 : 2,
                minHeight: 48,
                cursor: "pointer",
                "&.Mui-selected": {
                  bgcolor: "rgba(255,255,255,0.1)",
                  color: "#FFFFFF",
                  borderLeft: "4px solid #60A5FA",
                  "& .MuiListItemIcon-root": { color: "#60A5FA" },
                  "&:hover": { bgcolor: "rgba(255,255,255,0.15)" },
                },
                "&:hover": {
                  bgcolor: "rgba(255,255,255,0.04)",
                }
              }}
            >
              <ListItemIcon
                sx={{
                  minWidth: isCollapsed ? 0 : 36,
                  display: "flex",
                  justifyContent: "center",
                  color: isActive(item.path) ? "#FFFFFF" : "#BFDBFE",
                  transition: "color 0.2s",
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
                    color: isActive(item.path) ? "#FFFFFF" : "#DBEAFE",
                  },
                  }}
                />
              )}
            </ListItemButton>
          </Tooltip>
        ))}
      </List>

      <Divider />

      {/* Settings at the bottom */}
      {(hasPermission("user:manage") || hasPermission("connection:view") || hasPermission("model_config:view")) && (
        <List sx={{ px: 1, pb: 1, pt: 0.5 }}>
          <Tooltip title={isCollapsed ? "Settings" : ""} placement="right">
            <ListItemButton
              selected={location.pathname.startsWith("/app/settings")}
              onClick={() => navigate("/app/settings")}
              sx={{
                borderRadius: `${theme.datagate.radii.md}px`,
                justifyContent: isCollapsed ? "center" : "flex-start",
                px: isCollapsed ? 0 : 1.5,
                minHeight: 42,
                cursor: "pointer",
                "&.Mui-selected": {
                  bgcolor: "rgba(255,255,255,0.14)",
                  color: "#FFFFFF",
                },
              }}
            >
              <ListItemIcon
                sx={{
                  minWidth: isCollapsed ? 0 : 36,
                  display: "flex",
                  justifyContent: "center",
                  color: location.pathname.startsWith("/app/settings") ? "#FFFFFF" : "#BFDBFE",
                }}
              >
                <SettingsIcon />
              </ListItemIcon>
              {!isCollapsed && (
                <ListItemText
                  primary="Settings"
                  slotProps={{
                    primary: {
                      fontSize: "0.875rem",
                      fontWeight: location.pathname.startsWith("/app/settings") ? 700 : 500,
                      color: location.pathname.startsWith("/app/settings") ? "#FFFFFF" : "#DBEAFE",
                    },
                  }}
                />
              )}
            </ListItemButton>
          </Tooltip>
        </List>
      )}
    </Box>
  );
};

export default SideBar;
