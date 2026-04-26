import React from 'react';
import {
  Box, Typography, Grid, Paper, IconButton, Chip
} from '@mui/material';
import {
  Storage as StorageIcon,
  Group as GroupIcon,
  ManageAccounts as AccountIcon,
  Shield as RolesIcon,
  ArrowBack as BackIcon,
} from '@mui/icons-material';
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import Connection from './Connection/Connection';
import UserList from './Users/UserList';
import PasswordChange from './Security/PasswordChange';
import RoleManagement from './Roles/RoleManagement';
import { pageShellSx } from '~/theme';

const SettingsCard = ({ title, description, icon, color, onClick }) => (
  <Paper
    elevation={0}
    onClick={onClick}
    sx={{
      p: 3,
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      borderRadius: '8px',
      border: '1px solid',
      borderColor: 'divider',
      cursor: 'pointer',
      transition: 'all 0.2s ease',
      '&:hover': {
        borderColor: 'primary.main',
        boxShadow: '0 4px 16px rgba(37,99,235,0.1)',
        transform: 'translateY(-2px)',
      },
    }}
  >
    <Box
      sx={{
        bgcolor: `${color}.main`,
        borderRadius: '10px',
        opacity: 0.12,
        width: 52,
        height: 52,
        position: 'absolute',
      }}
    />
    <Box
      sx={{
        width: 52,
        height: 52,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        mb: 2.5,
        bgcolor: `${color}.50`,
        borderRadius: '10px',
        color: `${color}.main`,
      }}
    >
      {React.cloneElement(icon, { sx: { fontSize: 26 } })}
    </Box>
    <Typography variant="subtitle1" fontWeight={700} sx={{ mb: 0.75 }}>
      {title}
    </Typography>
    <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.6 }}>
      {description}
    </Typography>
  </Paper>
);

const SettingsDashboard = () => {
  const navigate = useNavigate();

  const categories = [
    {
      title: 'Connections',
      description: 'Configure lakehouse connections: Trino, Iceberg REST Catalog, MinIO.',
      icon: <StorageIcon />,
      color: 'secondary',
      path: '/settings/connection',
    },
    {
      title: 'Users',
      description: 'Manage user accounts, activation, and role assignments.',
      icon: <GroupIcon />,
      color: 'error',
      path: '/settings/users',
    },
    {
      title: 'Roles & Permissions',
      description: 'Configure system roles and assign permission codes to control access.',
      icon: <RolesIcon />,
      color: 'warning',
      path: '/settings/roles',
    },
    {
      title: 'Account Settings',
      description: 'Update your personal profile and change your password.',
      icon: <AccountIcon />,
      color: 'primary',
      path: '/settings/account',
    },
  ];

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight={800} mb={0.5}>Settings</Typography>
        <Typography variant="body1" color="text.secondary">
          Configure users, roles, connections, and platform preferences.
        </Typography>
      </Box>

      <Grid container spacing={3} alignItems="stretch">
        {categories.map((cat) => (
          <Grid item xs={12} sm={6} lg={3} key={cat.title} sx={{ position: 'relative' }}>
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
    <Box sx={pageShellSx}>
      {!isBasePage && (
        <Box sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 2 }}>
          <IconButton
            onClick={() => navigate('/settings')}
            size="small"
            sx={{ bgcolor: 'background.paper', border: '1px solid', borderColor: 'divider' }}
          >
            <BackIcon fontSize="small" />
          </IconButton>
          <Typography variant="h5" fontWeight={800}>Settings</Typography>
        </Box>
      )}

      <Routes>
        <Route index element={<SettingsDashboard />} />
        <Route path="connection/*" element={<Connection />} />
        <Route path="users" element={<UserList />} />
        <Route path="roles" element={<RoleManagement />} />
        <Route path="account" element={<PasswordChange />} />
        <Route path="security" element={<PasswordChange />} />
      </Routes>
    </Box>
  );
};

export default Settings;
