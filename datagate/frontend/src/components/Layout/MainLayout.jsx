import React from 'react';
import { Outlet } from 'react-router-dom';
import { Box } from '@mui/material';
import AppBar from '~/components/AppBar/AppBar';
import SideBar from '~/components/SideBar/SideBar';

const MainLayout = () => {
  const [isCollapsed, setIsCollapsed] = React.useState(false);

  const toggleSidebar = () => {
    setIsCollapsed(!isCollapsed);
  };

  return (
    <Box sx={{ display: 'flex', height: '100vh', overflow: 'hidden', bgcolor: 'background.default' }}>
      <SideBar isCollapsed={isCollapsed} onToggle={toggleSidebar} />
      
      <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
        <AppBar onToggleSidebar={toggleSidebar} isSidebarCollapsed={isCollapsed} />
        
        <Box 
          component="main" 
          sx={{ 
            flexGrow: 1, 
            overflow: 'auto',
            display: 'flex',
            flexDirection: 'column'
          }}
        >
          <Outlet />
        </Box>
      </Box>
    </Box>
  );
};

export default MainLayout;
