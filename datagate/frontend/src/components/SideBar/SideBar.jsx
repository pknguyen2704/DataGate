import React from "react";
import {
  Box,
  Typography,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Tooltip,
  Badge,
  Divider,
} from "@mui/material";
import {
  DashboardOutlined as DashboardIcon,
  TableChartOutlined as TablesIcon,
  PowerOutlined as ConnectionsIcon,
  RuleOutlined as RulesIcon,
  NotificationsNoneOutlined as AlertsIcon,
  WorkHistoryOutlined as JobsIcon,
  SettingsOutlined as SettingsIcon,
} from "@mui/icons-material";
import { useTheme } from "@mui/material/styles";
import { useNavigate, useLocation } from "react-router-dom";
import { useSelector } from "react-redux";
import DataGateLogo from "~/assets/images/datagate.svg";

const getNavItems = (openAlertCount) => [
  {
    text: "Home",
    icon: <DashboardIcon />,
    path: "/home",
    permission: "dashboard:view",
  },
  {
    text: "Tables",
    icon: <TablesIcon />,
    path: "/tables",
    permission: "table:view",
  },

  {
    text: "Rules",
    icon: <RulesIcon />,
    path: "/rules",
    permission: "rule:view",
  },
  {
    text: "Alerts",
    icon: (
      <Badge
        badgeContent={openAlertCount}
        color="error"
        max={99}
        sx={{ "& .MuiBadge-badge": { fontSize: "0.6rem", minWidth: 16, height: 16 } }}
      >
        <AlertsIcon />
      </Badge>
    ),
    path: "/alerts",
    permission: "alert:view",
  },
  {
    text: "Jobs",
    icon: <JobsIcon />,
    path: "/jobs",
    permission: "job:view",
  },
];

const SideBar = ({ isCollapsed }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const { user } = useSelector((state) => state.auth);
  const permissions = user?.permissions || [];

  // TODO: get real open alert count from Redux store
  const openAlertCount = 0;
  const navItems = getNavItems(openAlertCount);

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
        bgcolor: "background.paper",
        transition: "width 0.25s cubic-bezier(0.4,0,0.2,1), min-width 0.25s cubic-bezier(0.4,0,0.2,1)",
        overflowX: "hidden",
        borderRight: "1px solid",
        borderColor: "divider",
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
              color: "primary.main",
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
                mb: 0.5,
                borderRadius: 1,
                justifyContent: isCollapsed ? "center" : "flex-start",
                px: isCollapsed ? 0 : 1.5,
                minHeight: 42,
                cursor: "pointer",
                "&.Mui-selected": {
                  bgcolor: "#EFF6FF",
                  color: "primary.main",
                  "&:hover": { bgcolor: "#DBEAFE" },
                },
              }}
            >
              <ListItemIcon
                sx={{
                  minWidth: isCollapsed ? 0 : 36,
                  display: "flex",
                  justifyContent: "center",
                  color: isActive(item.path) ? "primary.main" : "text.secondary",
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
      <List sx={{ px: 1, pb: 1, pt: 0.5 }}>
        <Tooltip title={isCollapsed ? "Settings" : ""} placement="right">
          <ListItemButton
            selected={location.pathname.startsWith("/settings")}
            onClick={() => navigate("/settings")}
            sx={{
              borderRadius: 1,
              justifyContent: isCollapsed ? "center" : "flex-start",
              px: isCollapsed ? 0 : 1.5,
              minHeight: 42,
              cursor: "pointer",
              "&.Mui-selected": {
                bgcolor: "#EFF6FF",
                color: "primary.main",
              },
            }}
          >
            <ListItemIcon
              sx={{
                minWidth: isCollapsed ? 0 : 36,
                display: "flex",
                justifyContent: "center",
                color: location.pathname.startsWith("/settings") ? "primary.main" : "text.secondary",
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
                    fontWeight: location.pathname.startsWith("/settings") ? 700 : 500,
                  },
                }}
              />
            )}
          </ListItemButton>
        </Tooltip>
      </List>
    </Box>
  );
};

export default SideBar;
