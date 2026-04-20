import React from 'react';
import { 
  Box, Typography, Grid, Paper, Divider
} from '@mui/material';
import { 
  SettingsSuggest as ConfigIcon,
  TableRows as TablesIcon
} from '@mui/icons-material';
import { useNavigate, Routes, Route } from 'react-router-dom';
import ConnectConfig from './ConnectConfig/ConnectConfig';
import TablesManagement from './TablesManagement/TablesManagement';

const ShortcutCard = ({ title, description, icon, color, onClick }) => (
  <Paper 
    elevation={0}
    onClick={onClick}
    sx={{ 
      p: 4, 
      display: 'flex', 
      flexDirection: 'column',
      height: '100%',
      borderRadius: 4, 
      border: '1px solid',
      borderColor: 'divider',
      cursor: 'pointer',
      transition: 'all 0.2s ease-in-out',
      '&:hover': {
        borderColor: 'primary.main',
        boxShadow: '0 8px 24px rgba(0,0,0,0.06)',
        transform: 'translateY(-4px)',
        '& .icon-circle': {
          bgcolor: `${color}.main`,
          color: 'white',
        }
      }
    }}
  >
    <Box 
      className="icon-circle"
      sx={{ 
        bgcolor: `${color}.light`,
        borderRadius: 3,
        color: `${color}.main`,
        width: 64,
        height: 64,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        mb: 3,
        transition: 'all 0.2s ease-in-out',
      }}
    >
      {React.cloneElement(icon, { sx: { fontSize: 32 } })}
    </Box>
    <Typography variant="h5" fontWeight="900" sx={{ mb: 1.5 }}>
      {title}
    </Typography>
    <Typography variant="body1" color="text.secondary" sx={{ lineHeight: 1.6 }}>
      {description}
    </Typography>
  </Paper>
);

const ConnectionDashboard = () => {
    const navigate = useNavigate();
    return (
        <Box>
            <Box sx={{ mb: 4 }}>
                <Typography variant="h4" fontWeight="900">Connect Management</Typography>
                <Typography variant="body1" color="text.secondary">Configure your infrastructure and manage metadata ingestion from your data lakehouse.</Typography>
            </Box>
            
            <Grid container spacing={4}>
                <Grid item xs={12} md={6}>
                    <ShortcutCard 
                        title="Configuration" 
                        description="Manage Trino engine connection details, authentication, and credentials."
                        icon={<ConfigIcon />}
                        color="secondary"
                        onClick={() => navigate('config')}
                    />
                </Grid>
                <Grid item xs={12} md={6}>
                    <ShortcutCard 
                        title="Table Management" 
                        description="Select and integrate specific tables from Iceberg catalogs for observability."
                        icon={<TablesIcon />}
                        color="primary"
                        onClick={() => navigate('tables')}
                    />
                </Grid>
            </Grid>
        </Box>
    );
}

const Connection = () => {
  return (
    <Routes>
      <Route index element={<ConnectionDashboard />} />
      <Route path="config" element={<ConnectConfig />} />
      <Route path="tables" element={<TablesManagement />} />
    </Routes>
  );
};

export default Connection;
