import { Outlet, useLocation } from 'react-router-dom';
import { Box, Container } from '@mui/material';
import AppBar from '~/components/AppBar/AppBar';
import Footer from '~/components/Footer/Footer';
import SideBar from '~/components/SideBar/SideBar';

const MainLayout = () => {
  return (
    <Box sx={{ display: 'flex', height: '100vh', overflow: 'hidden', bgcolor: 'background.default' }}>
      <SideBar />
      
      <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
        <AppBar />
        
        <Box 
          component="main" 
          sx={{ 
            flexGrow: 1, 
            p: 3, 
            overflow: 'auto',
            display: 'flex',
            flexDirection: 'column'
          }}
        >
          <Outlet />
        </Box>
        <Footer />
      </Box>
    </Box>
  );
};

export default MainLayout;
