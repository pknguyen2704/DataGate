import React, { useState } from 'react';
import { 
  Box, Typography, Tabs, Tab, Paper, IconButton
} from '@mui/material';
import { 
  Group as UsersIcon,
  Shield as RolesIcon,
  ArrowBack as BackIcon
} from '@mui/icons-material';
import { useNavigate, useSearchParams } from 'react-router-dom';
import UserList from './UserList/UserList';
import RoleManagement from './RoleManagement/RoleManagement';

const UserManagement = () => {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  
  const initialTab = parseInt(searchParams.get('tab') || '0');
  const [activeTab, setActiveTab] = useState(initialTab);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
    setSearchParams({ tab: newValue });
  };

  return (
    <Box>
      <Box sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 2 }}>
        <IconButton onClick={() => navigate('/settings')} size="small">
          <BackIcon />
        </IconButton>
        <Typography variant="h4" fontWeight="900">
          User Management
        </Typography>
      </Box>

      <Paper sx={{ mb: 4, borderRadius: 2, overflow: 'hidden', bgcolor: 'transparent' }} elevation={0}>
        <Tabs 
          value={activeTab} 
          onChange={handleTabChange} 
          sx={{ 
            borderBottom: 1, 
            borderColor: 'divider',
            px: 2,
            bgcolor: '#F8FAFC'
          }}
        >
          <Tab 
            icon={<UsersIcon fontSize="small" />} 
            iconPosition="start" 
            label="Users" 
            sx={{ fontWeight: 700, minHeight: 60 }}
          />
          <Tab 
            icon={<RolesIcon fontSize="small" />} 
            iconPosition="start" 
            label="Roles & Permissions" 
            sx={{ fontWeight: 700, minHeight: 60 }}
          />
        </Tabs>

        <Box sx={{ py: 4 }}>
          {activeTab === 0 && <UserList />}
          {activeTab === 1 && <RoleManagement />}
        </Box>
      </Paper>
    </Box>
  );
};

export default UserManagement;
