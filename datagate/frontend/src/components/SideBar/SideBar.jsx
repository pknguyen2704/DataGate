import React from "react";
import {
  Box,
  Typography,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  Tooltip,
} from "@mui/material";
import {
  DashboardOutlined as DashboardIcon,
  VisibilityOutlined as ObservabilityIcon,
  FactCheckOutlined as RulesIcon,
  AssessmentOutlined as MetricsIcon,
  AutoGraphOutlined as AnomalyIcon,
  AccountTreeOutlined as LineageIcon,
  SearchOutlined as ExplorerIcon,
  SettingsOutlined as SettingsIcon,
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
} from "@mui/icons-material";
import { useTheme } from "@mui/material/styles";
import { useNavigate, useLocation } from "react-router-dom";

const navItems = [
  { text: "Overview", icon: <DashboardIcon />, path: "/home" },
  { text: "Data Observability", icon: <ObservabilityIcon />, path: "/observability" },
  { text: "Rule Validation", icon: <RulesIcon />, path: "/rules" },
  { text: "Metric Monitoring", icon: <MetricsIcon />, path: "/metrics" },
  { text: "ML Anomaly Detection", icon: <AnomalyIcon />, path: "/anomaly" },
  { text: "Data Lineage", icon: <LineageIcon />, path: "/lineage" },
  { text: "Dataset Explorer", icon: <ExplorerIcon />, path: "/explorer" },
  { text: "Settings", icon: <SettingsIcon />, path: "/settings" },
];

const SideBar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const [isCollapsed, setIsCollapsed] = React.useState(false);

  const isActive = (path) => {
    if (path === "/home" && location.pathname === "/home") return true;
    if (path !== "/home" && location.pathname.startsWith(path)) return true;
    return false;
  };

  return (
    <Box
      sx={{
        width: isCollapsed ? "80px" : theme.datagate.sidebarWidth,
        height: "100%",
        display: "flex",
        flexDirection: "column",
        bgcolor: "background.paper",
        borderRight: "1px solid",
        borderColor: "divider",
        transition: "width 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
        overflowX: "hidden",
        zIndex: 1200,
      }}
    >
      {/* Brand Logo Area */}
      <Box sx={{ p: 3, display: 'flex', alignItems: 'center', minHeight: '80px' }}>
        <Box 
          className="gradient-blue" 
          sx={{ 
            width: 32, 
            height: 32, 
            borderRadius: '8px', 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            color: 'white',
            fontWeight: 800,
            fontSize: '18px',
            mr: isCollapsed ? 0 : 2
          }}
        >
          D
        </Box>
        {!isCollapsed && (
          <Typography variant="h6" sx={{ fontWeight: 800, color: 'primary.main', letterSpacing: '-0.5px' }}>
            DataGate
          </Typography>
        )}
      </Box>

      {/* Navigation List */}
      <List sx={{ flexGrow: 1, px: 1 }}>
        {navItems.map((item) => (
          <Tooltip key={item.text} title={isCollapsed ? item.text : ""} placement="right">
            <ListItemButton
              selected={isActive(item.path)}
              onClick={() => navigate(item.path)}
              sx={{
                mb: 0.5,
                justifyContent: isCollapsed ? "center" : "flex-start",
                px: isCollapsed ? 1 : 2,
              }}
            >
              <ListItemIcon 
                sx={{ 
                  minWidth: isCollapsed ? 0 : 40,
                  mr: isCollapsed ? 0 : 0,
                  color: isActive(item.path) ? "primary.main" : "text.secondary"
                }}
              >
                {item.icon}
              </ListItemIcon>
              {!isCollapsed && (
                <ListItemText 
                  primary={item.text} 
                  primaryTypographyProps={{ 
                    fontSize: '0.875rem', 
                    fontWeight: isActive(item.path) ? 600 : 500 
                  }} 
                />
              )}
            </ListItemButton>
          </Tooltip>
        ))}
      </List>

      {/* User / Bottom Section */}
      <Box sx={{ p: 2, borderTop: '1px solid', borderColor: 'divider' }}>
        <ListItemButton 
          onClick={() => setIsCollapsed(!isCollapsed)}
          sx={{ justifyContent: isCollapsed ? "center" : "flex-start" }}
        >
          <ListItemIcon sx={{ minWidth: isCollapsed ? 0 : 40 }}>
            {isCollapsed ? <ChevronRightIcon /> : <ChevronLeftIcon />}
          </ListItemIcon>
          {!isCollapsed && (
            <ListItemText 
              primary="Collapse Sidebar" 
              primaryTypographyProps={{ fontSize: '0.875rem', fontWeight: 500 }} 
            />
          )}
        </ListItemButton>
      </Box>
    </Box>
  );
};

export default SideBar;
