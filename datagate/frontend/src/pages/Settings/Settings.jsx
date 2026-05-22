import { Box, Typography, Paper, List, ListItemButton, ListItemIcon, ListItemText, Divider } from "@mui/material";
import { SettingsInputComponentOutlined, ModelTrainingOutlined, PeopleOutlined } from "@mui/icons-material";
import { Outlet, useLocation, useNavigate } from "react-router-dom";
import { useEffect, useMemo } from "react";
import { useRBAC } from "~/rbac/useRBAC";
import { PermissionCode } from "~/rbac/permission";

const SETTINGS_BASE_PATH = "/app/settings";

const SETTINGS_MENU = [
  {
    text: "Platform Connections",
    icon: <SettingsInputComponentOutlined />,
    path: `${SETTINGS_BASE_PATH}/connections`,
    permission: PermissionCode.CONNECTION_MANAGE,
  },
  {
    text: "Anomaly Configurations",
    icon: <ModelTrainingOutlined />,
    path: `${SETTINGS_BASE_PATH}/anomaly-configs`,
    permission: PermissionCode.ANOMALY_CONFIG_MANAGE,
  },
  {
    text: "Users",
    icon: <PeopleOutlined />,
    path: `${SETTINGS_BASE_PATH}/users`,
    permission: PermissionCode.USER_MANAGE,
  },
];

const settingsShellSx = {
  display: "flex",
  height: "100%",
  p: 3,
  gap: 3,
};

const settingsNavSx = {
  width: 280,
  flexShrink: 0,
  height: "fit-content",
  borderRadius: 2,
  border: "1px solid",
  borderColor: "divider",
  boxShadow: "0 4px 20px rgba(0,0,0,0.03)",
};

const navItemSx = {
  borderRadius: 1.5,
  mb: 0.5,
  "&.Mui-selected": {
    color: "primary.main",
    bgcolor: "rgba(37, 99, 235, 0.08)",
    "& .MuiListItemIcon-root": {
      color: "primary.main",
    },
    "&:hover": {
      bgcolor: "rgba(37, 99, 235, 0.12)",
    },
  },
};

const SettingsPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { hasPermission } = useRBAC();

  const visibleItems = useMemo(
    () => SETTINGS_MENU.filter((item) => hasPermission(item.permission)),
    [hasPermission]
  );

  useEffect(() => {
    if (location.pathname === SETTINGS_BASE_PATH && visibleItems.length > 0) {
      navigate(visibleItems[0].path, { replace: true });
    }
  }, [location.pathname, visibleItems, navigate]);

  return (
    <Box sx={settingsShellSx}>
      <Paper sx={settingsNavSx}>
        <Box sx={{ p: 2.5 }}>
          <Typography variant="h6" fontWeight={800}>
            Settings
          </Typography>
        </Box>
        <Divider />
        <List sx={{ p: 1 }}>
          {visibleItems.map((item) => (
            <ListItemButton
              key={item.text}
              selected={location.pathname === item.path}
              onClick={() => navigate(item.path)}
              sx={navItemSx}
            >
              <ListItemIcon sx={{ minWidth: 40 }}>{item.icon}</ListItemIcon>
              <ListItemText
                primary={
                  <Typography variant="body2" fontWeight={600}>
                    {item.text}
                  </Typography>
                }
              />
            </ListItemButton>
          ))}
        </List>
      </Paper>

      <Box sx={{ flexGrow: 1, minWidth: 0 }}>
        <Outlet />
      </Box>
    </Box>
  );
};

export default SettingsPage;
