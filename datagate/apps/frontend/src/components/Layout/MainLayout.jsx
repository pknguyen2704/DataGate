import { Outlet, useLocation } from 'react-router-dom';
import { Box, Container } from '@mui/material';
import AppBar from '~/components/AppBar/AppBar';
import Footer from '~/components/Footer/Footer';
import SideBar from '~/components/SideBar/SideBar';

const MainLayout = () => {
  const location = useLocation();
  // Sidebar should only appear for Data Profiling, Rules, and Anomaly Detection
  const dataPages = ['/profiling', '/rules', '/anomaly'];
  const showSidebar = dataPages.some(page => location.pathname.startsWith(page));

  return (
    <Container disableGutters maxWidth={false} sx={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      <AppBar />
      <Box sx={{ display: 'flex', flexGrow: 1, pt: '64px', overflow: 'hidden' }}>
        {showSidebar && <SideBar />}
        
        <Box component="main" sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', overflow: 'auto'}}>
          <Outlet />
        </Box>
      </Box>
      <Footer />
    </Container>
  );
};

export default MainLayout;
