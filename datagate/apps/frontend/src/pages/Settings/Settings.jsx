import React from 'react';
import { 
  Box, Typography, List, ListItem, ListItemButton, 
  ListItemIcon, ListItemText, Divider, Container, 
  Breadcrumbs, Link as MuiLink
} from '@mui/material';
import { 
  Storage as StorageIcon, 
  SettingsRounded as SettingsIcon,
  Link as LinkIcon,
  Person as PersonIcon,
  Security as SecurityIcon,
  BrandingWatermark as BrandIcon
} from '@mui/icons-material';
import { Routes, Route, useNavigate, useLocation, Link } from 'react-router-dom';
import ServiceList from './Services/ServiceList';

const Settings = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    { text: 'Services', icon: <StorageIcon />, path: '/settings/services' },
    { text: 'Users', icon: <PersonIcon />, path: '/settings/users', disabled: true },
    { text: 'Security', icon: <SecurityIcon />, path: '/settings/security', disabled: true },
    { text: 'Branding', icon: <BrandIcon />, path: '/settings/branding', disabled: true },
  ];

  return (
    <Container disableGutters maxWidth={false} sx={{ display: 'flex', flexDirection: 'column', height: (theme) => theme.datagate.mainContentHeight }}>
      {/* Settings Header / Breadcrumbs */}
      <Box sx={{ p: 2, px: 3, borderBottom: '1px solid', borderColor: 'divider', bgcolor: 'white' }}>
        <Breadcrumbs aria-label="breadcrumb">
          <MuiLink component={Link} underline="hover" color="inherit" to="/">DataGate</MuiLink>
          <MuiLink component={Link} underline="hover" color="inherit" to="/settings">Settings</MuiLink>
          {location.pathname.includes('/services') && (
            <Typography color="text.primary">Services</Typography>
          )}
        </Breadcrumbs>
      </Box>

      <Box sx={{ display: 'flex', flexGrow: 1, overflow: 'hidden' }}>
        {/* Settings Sidebar */}
        <Box sx={{ 
          width: 280, 
          borderRight: '1px solid', 
          borderColor: 'divider', 
          bgcolor: '#FBFCFE',
          display: 'flex',
          flexDirection: 'column'
        }}>
          <Box sx={{ p: 3 }}>
            <Typography variant="h6" fontWeight="700" color="text.primary">Settings</Typography>
            <Typography variant="caption" color="text.secondary">Global configurations and integrations</Typography>
          </Box>
          <Divider />
          <List sx={{ px: 1, mt: 1 }}>
            {menuItems.map((item) => (
              <ListItem key={item.text} disablePadding sx={{ mb: 0.5 }}>
                <ListItemButton 
                  selected={location.pathname.startsWith(item.path)}
                  onClick={() => !item.disabled && navigate(item.path)}
                  disabled={item.disabled}
                  sx={{ 
                    borderRadius: 2,
                    '&.Mui-selected': { 
                      bgcolor: 'primary.main', 
                      color: 'white',
                      '& .MuiListItemIcon-root': { color: 'white' }
                    }
                  }}
                >
                  <ListItemIcon sx={{ minWidth: 40, color: location.pathname.startsWith(item.path) ? 'white' : 'text.secondary' }}>
                    {item.icon}
                  </ListItemIcon>
                  <ListItemText primary={item.text} primaryTypographyProps={{ fontSize: '0.9rem', fontWeight: 600 }} />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
        </Box>

        {/* Settings Content */}
        <Box sx={{ flexGrow: 1, bgcolor: '#F8FAFC', overflow: 'auto', p: 4 }}>
          <Routes>
            <Route path="services" element={<ServiceList />} />
            <Route path="*" element={<Box sx={{ display: 'flex', justifyContent: 'center', mt: 10 }}><Typography color="text.secondary">Select a setting category from the left</Typography></Box>} />
          </Routes>
        </Box>
      </Box>
    </Container>
  );
};

export default Settings;
