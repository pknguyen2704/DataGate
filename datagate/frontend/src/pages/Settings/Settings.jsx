import React from "react";
import { Box, Typography, Paper, List, ListItemButton, ListItemIcon, ListItemText, Divider } from "@mui/material";
import { SettingsInputComponentOutlined, ModelTrainingOutlined, PeopleOutlined, ShieldOutlined } from "@mui/icons-material";
import { useNavigate, useLocation, Outlet } from "react-router-dom";
import { useSelector } from "react-redux";
import UserManagement from "./UserManagement/UserManagement";
import RoleManagement from "./RoleManagement/RoleManagement";

const SettingsPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useSelector((state) => state.auth);
  const permissions = user?.permissions || [];

  const hasPermission = (permCode) => {
    if (!permCode) return true;
    const isAdmin = user?.roles?.some(r => r === "Admin" || r?.name === "Admin");
    if (isAdmin) return true;
    return permissions.some(p => p === permCode || p?.code === permCode);
  };

  const menuItems = [
    { text: "Platform Connections", icon: <SettingsInputComponentOutlined />, path: "/app/settings/connections", permission: "connection:view" },
    { text: "Model parameters", icon: <ModelTrainingOutlined />, path: "/app/settings/model-configs", permission: "model_config:view" },
    { text: "Users", icon: <PeopleOutlined />, path: "/app/settings/users", permission: "user:view" },
    { text: "Roles", icon: <ShieldOutlined />, path: "/app/settings/roles", permission: "user:view" },
  ];

  const visibleItems = menuItems.filter(item => hasPermission(item.permission));

  React.useEffect(() => {
    if (location.pathname === "/app/settings" && visibleItems.length > 0) {
      navigate(visibleItems[0].path, { replace: true });
    }
  }, [location.pathname, visibleItems, navigate]);

  return (
    <Box sx={{ display: 'flex', height: '100%', p: 3, gap: 3 }}>
      <Paper sx={{ width: 280, flexShrink: 0, borderRadius: 2, height: 'fit-content', border: '1px solid', borderColor: 'divider', boxShadow: '0 4px 20px rgba(0,0,0,0.03)' }}>
        <Box sx={{ p: 2.5 }}>
          <Typography variant="h6" fontWeight={800}>Settings</Typography>
        </Box>
        <Divider />
        <List sx={{ p: 1 }}>
          {visibleItems.map((item) => (
            <ListItemButton
              key={item.text}
              selected={location.pathname === item.path}
              onClick={() => navigate(item.path)}
              sx={{
                borderRadius: 1.5,
                mb: 0.5,
                '&.Mui-selected': {
                  bgcolor: 'primary.50',
                  color: 'primary.main',
                  '& .MuiListItemIcon-root': { color: 'primary.main' },
                  '&:hover': { bgcolor: 'primary.100' }
                }
              }}
            >
              <ListItemIcon sx={{ minWidth: 40 }}>{item.icon}</ListItemIcon>
              <ListItemText primary={<Typography variant="body2" fontWeight={600}>{item.text}</Typography>} />
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

export { UserManagement as UsersPlaceholder, RoleManagement as RolesPlaceholder };
export const ConnectionsPlaceholder = () => <Typography variant="h5">Connections Management</Typography>;
export const ModelConfigsPlaceholder = () => <Typography variant="h5">Model Configurations</Typography>;
