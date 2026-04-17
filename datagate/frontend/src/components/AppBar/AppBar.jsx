import React from "react";
import {
  AppBar as MuiAppBar,
  Toolbar,
  Box,
  Typography,
  IconButton,
  Tooltip,
  Avatar,
  Menu,
  MenuItem,
  Divider,
  ListItemIcon,
} from "@mui/material";
import {
  NotificationsNoneOutlined as NotificationsIcon,
  Logout as LogoutIcon,
  PersonOutline as PersonIcon,
  HelpOutline as HelpIcon,
  Menu as MenuIcon,
  MenuOpen as MenuOpenIcon,
} from "@mui/icons-material";
import { useDispatch, useSelector } from "react-redux";
import { logout as logoutAction } from "../../stores/slices/authSlice";
import { useNavigate } from "react-router-dom";

const AppBar = ({ onToggleSidebar, isSidebarCollapsed }) => {
  const dispatch = useDispatch();
  const { user } = useSelector((state) => state.auth);
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = React.useState(null);

  const handleProfileClick = (event) => setAnchorEl(event.currentTarget);
  const handleClose = () => setAnchorEl(null);
  const handleLogout = () => {
    handleClose();
    dispatch(logoutAction());
    navigate("/auth/login");
  };

  return (
    <MuiAppBar
      position="static"
      elevation={0}
      sx={{
        bgcolor: "transparent",
        border: "none",
        borderBottom: 1,
        borderBottomColor: "divider",
        borderRadius: 0,
      }}
    >
      <Toolbar sx={{ justifyContent: "space-between", minHeight: "64px", gap: 2 }}>
        <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
          <IconButton
            onClick={onToggleSidebar}
            edge="start"
            sx={{
              color: "text.primary",
              bgcolor: "transparent",
              "&:hover": { bgcolor: "action.hover" },
            }}
          >
            {isSidebarCollapsed ? <MenuIcon /> : <MenuOpenIcon />}
          </IconButton>
        </Box>

        <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
          <Tooltip title="Documentation">
            <IconButton size="small">
              <HelpIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          
          <Tooltip title="Notifications">
            <IconButton size="small">
              <NotificationsIcon fontSize="small" />
            </IconButton>
          </Tooltip>

          <Divider orientation="vertical" flexItem sx={{ mx: 1, height: 24, alignSelf: "center" }} />

          <Box
            sx={{
              display: "flex",
              alignItems: "center",
              gap: 1.5,
              cursor: "pointer",
              ml: 1,
              px: 1,
              py: 0.5,
              borderRadius: 2.5,
              "&:hover": { bgcolor: "action.hover" },
            }}
            onClick={handleProfileClick}
          >
            <Box sx={{ textAlign: "right", display: { xs: "none", md: "block" } }}>
              <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 600, lineHeight: 1.2 }}>
                {user?.full_name || user?.username || "User"}
              </Typography>
              {user?.username && (
                <Typography variant="caption" color="text.secondary" sx={{ lineHeight: 1 }}>
                  @{user.username}
                </Typography>
              )}
            </Box>
            <Avatar sx={{ width: 36, height: 36, bgcolor: "primary.main", fontSize: "0.875rem", fontWeight: 700 }}>
              {(user?.full_name || user?.username || "User").charAt(0).toUpperCase()}
            </Avatar>
          </Box>
        </Box>

        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleClose}
          transformOrigin={{ horizontal: 'right', vertical: 'top' }}
          anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
          PaperProps={{
            elevation: 3,
            sx: { mt: 1.5, borderRadius: 2, minWidth: 200 },
          }}
        >
          <MenuItem onClick={handleClose}>
            <ListItemIcon><PersonIcon fontSize="small" /></ListItemIcon>
            Account Profile
          </MenuItem>
          <Divider />
          <MenuItem onClick={handleLogout} sx={{ color: 'error.main' }}>
            <ListItemIcon><LogoutIcon fontSize="small" sx={{ color: 'error.main' }} /></ListItemIcon>
            Sign Out
          </MenuItem>
        </Menu>
      </Toolbar>
    </MuiAppBar>
  );
};

export default AppBar;
