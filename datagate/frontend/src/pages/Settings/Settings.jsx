import React from 'react';
import { 
  Box, Typography, Grid, Paper, Container, IconButton 
} from '@mui/material';
import { 
  Storage as StorageIcon, 
  Group as GroupIcon,
  ManageAccounts as AccountIcon,
  ArrowBack as BackIcon
} from '@mui/icons-material';
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import ServiceList from './Services/ServiceList';
import UserList from './Users/UserList';
import PasswordChange from './Security/PasswordChange';

const SettingsCard = ({ title, description, icon, color, onClick }) => (
  <Paper 
    elevation={0}
    onClick={onClick}
    sx={{ 
      p: 3, 
      display: 'flex', 
      flexDirection: 'column',
      height: '100%',
      borderRadius: '4px', 
      border: '1px solid',
      borderColor: 'divider',
      cursor: 'pointer',
      transition: 'all 0.2s ease-in-out',
      position: 'relative',
      overflow: 'hidden',
      '&:hover': {
        borderColor: 'primary.main',
        boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
        '& .icon-box': {
          transform: 'scale(1.05)',
          bgcolor: `${color}.main`,
          color: 'white',
        }
      }
    }}
  >
    <Box 
      className="icon-box"
      sx={{ 
        bgcolor: `${color}.light`,
        borderRadius: '200px',
        color: `${color}.main`,
        opacity: 0.9,
        width: 56,
        height: 56,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        mb: 2.5,
        transition: 'all 0.2s ease-in-out',
      }}
    >
      {React.cloneElement(icon, { sx: { fontSize: 28 } })}
    </Box>
    <Box sx={{ flexGrow: 1 }}>
      <Typography variant="h6" fontWeight="600" sx={{ mb: 1, lineHeight: 1.2 }}>
        {title}
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.6 }}>
        {description}
      </Typography>
    </Box>
  </Paper>
);

const SettingsDashboard = () => {
  const navigate = useNavigate();
  
  const categories = [
    { 
      title: 'Services', 
      description: 'Set up connectors and ingest metadata from diverse sources including databases, warehouses, and data lakes.', 
      icon: <StorageIcon />, 
      color: 'secondary', 
      path: '/settings/services' 
    },
    { 
      title: 'Users', 
      description: 'Manage users, teams, and access permissions within the DataGate workspace.', 
      icon: <GroupIcon />, 
      color: 'error', 
      path: '/settings/users' 
    },
    { 
      title: 'Account Settings', 
      description: 'Update your personal profile, security credentials, and platform preferences.', 
      icon: <AccountIcon />, 
      color: 'primary', 
      path: '/settings/account' 
    },
  ];

  return (
    <Box>
      <Box sx={{ mb: 6 }}>
        <Typography variant="h4" fontWeight="700" sx={{ mb: 1.5, letterSpacing: '-0.02em' }}>
          Settings
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ maxWidth: 600 }}>
          Configure the DataGate platform to suit your data governance and observability requirements.
        </Typography>
      </Box>

      <Grid container spacing={4} alignItems="stretch">
        {categories.map((cat) => (
          <Grid item xs={12} md={6} lg={4} key={cat.title}>
            <SettingsCard {...cat} onClick={() => navigate(cat.path)} />
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

const Settings = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const isBasePage = location.pathname === '/settings' || location.pathname === '/settings/';

  return (
    <Box sx={{ flexGrow: 1, bgcolor: 'white', p: 4, height: '100%', overflow: 'auto' }}>
      {!isBasePage && (
        <Box sx={{ mb: 4, display: 'flex', alignItems: 'center', gap: 2 }}>
          <IconButton 
            onClick={() => navigate('/settings')} 
            sx={{ 
              bgcolor: 'white', 
              border: '1px solid', 
              borderColor: 'divider',
              borderRadius: '4px',
              '&:hover': { bgcolor: 'action.hover' }
            }}
          >
            <BackIcon fontSize="small" />
          </IconButton>
          <Typography variant="h5" fontWeight="800">Settings</Typography>
        </Box>
      )}

      <Routes>
        <Route index element={<SettingsDashboard />} />
        <Route path="services" element={<ServiceList />} />
        <Route path="users" element={<UserList />} />
        <Route path="account" element={<PasswordChange />} />
        <Route path="security" element={<PasswordChange />} /> 
      </Routes>
    </Box>
  );
};

export default Settings;


