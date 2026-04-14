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
  InputBase,
} from "@mui/material";
import {
  NotificationsNoneOutlined as NotificationsIcon,
  Search as SearchIcon,
  Logout as LogoutIcon,
  PersonOutline as PersonIcon,
  HelpOutline as HelpIcon,
} from "@mui/icons-material";
import { useAuth } from "../../contexts/AuthContext";
import { useNavigate } from "react-router-dom";

const AppBar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = React.useState(null);

  const handleProfileClick = (event) => setAnchorEl(event.currentTarget);
  const handleClose = () => setAnchorEl(null);
  const handleLogout = () => {
    handleClose();
    logout();
    navigate("/auth/login");
  };

  return (
    <MuiAppBar position="static" elevation={0} sx={{ borderBottom: '1px solid', borderColor: 'divider', bgcolor: 'transparent' }}>
      <Toolbar sx={{ justifyContent: "space-between", minHeight: '64px' }}>
        {/* Search Bar */}
        <Box 
          sx={{ 
            display: "flex", 
            alignItems: "center", 
            bgcolor: "#F1F5F9", 
            borderRadius: "8px", 
            px: 2, 
            py: 0.5,
            width: { xs: '200px', md: '400px' },
            transition: 'all 0.2s',
            '&:focus-within': {
              bgcolor: 'white',
              boxShadow: '0 0 0 2px #2563EB33',
              border: '1px solid #2563EB'
            }
          }}
        >
          <SearchIcon sx={{ color: "text.secondary", fontSize: 20, mr: 1 }} />
          <InputBase
            placeholder="Search datasets, rules, or alerts..."
            sx={{ flex: 1, fontSize: '0.875rem' }}
          />
        </Box>

        {/* Right side Actions */}
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

          <Divider orientation="vertical" flexItem sx={{ mx: 1, height: 24, alignSelf: 'center' }} />

          <Box 
            sx={{ 
              display: "flex", 
              alignItems: "center", 
              gap: 1.5, 
              cursor: "pointer",
              ml: 1,
              px: 1,
              py: 0.5,
              borderRadius: '8px',
              '&:hover': { bgcolor: '#F1F5F9' }
            }}
            onClick={handleProfileClick}
          >
            <Box sx={{ textAlign: 'right', display: { xs: 'none', md: 'block' } }}>
              <Typography variant="body2" sx={{ fontWeight: 600, lineHeight: 1 }}>
                {user?.full_name || 'Admin User'}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {user?.role || 'Data Engineer'}
              </Typography>
            </Box>
            <Avatar 
              sx={{ 
                width: 36, 
                height: 36, 
                bgcolor: 'primary.main',
                fontSize: '0.875rem',
                fontWeight: 700
              }}
            >
              {user?.email?.charAt(0).toUpperCase() || 'A'}
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
            sx: { mt: 1.5, borderRadius: '12px', minWidth: 200 }
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