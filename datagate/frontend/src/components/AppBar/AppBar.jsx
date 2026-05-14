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
import { datagateColors } from "~/theme";

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
    navigate("/login");
  };

  return (
    <MuiAppBar
      position="sticky"
      elevation={0}
      sx={{
        bgcolor: "#FFFFFF",
        borderBottom: "1px solid",
        borderBottomColor: "rgba(0, 0, 0, 0.08)",
        borderRadius: 0,
        zIndex: (theme) => theme.zIndex.drawer + 1,
      }}
    >
      <Toolbar sx={{ justifyContent: "space-between", minHeight: "64px", px: { xs: 2, md: 4 } }}>
        <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
          <IconButton
            onClick={onToggleSidebar}
            edge="start"
            sx={{
              color: "text.primary",
              bgcolor: "transparent",
              "&:hover": { bgcolor: "rgba(0, 0, 0, 0.04)" },
              transition: "all 0.2s ease"
            }}
          >
            {isSidebarCollapsed ? <MenuIcon /> : <MenuOpenIcon />}
          </IconButton>
        </Box>

        <Box sx={{ display: "flex", alignItems: "center", gap: 3 }}>
          <Box
            sx={{
              display: "flex",
              alignItems: "center",
              gap: 1.5,
              cursor: "pointer",
              px: 1.5,
              py: 0.5,
              borderRadius: "12px",
              transition: "all 0.2s ease",
              "&:hover": { bgcolor: "rgba(0, 0, 0, 0.04)" },
            }}
            onClick={handleProfileClick}
          >
            <Box sx={{ textAlign: "right", display: { xs: "none", md: "block" } }}>
              <Typography variant="body2" color="text.primary" sx={{ fontWeight: 700, lineHeight: 1.2 }}>
                {user?.full_name || user?.username || "User"}
              </Typography>
              <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 500 }}>
                {user?.username ? `@${user.username}` : "Administrator"}
              </Typography>
            </Box>
            <Avatar sx={{ width: 36, height: 36, bgcolor: "primary.main", fontSize: "0.875rem", fontWeight: 700, border: "2px solid #FFFFFF", boxShadow: "0 2px 8px rgba(37, 99, 235, 0.2)" }}>
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
