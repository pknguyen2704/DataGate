import React from 'react';
import { Box, Typography, Link, useTheme } from '@mui/material';

const Footer = () => {
  const theme = useTheme();

  return (
    <Box
      component="footer"
      sx={{
        py: 2,
        px: { xs: 2, md: 4 },
        mt: 'auto',
        backgroundColor: theme.palette.background.paper,
        borderTop: `1px solid ${theme.palette.divider}`,
        display: 'flex',
        flexDirection: { xs: 'column', sm: 'row' },
        alignItems: 'center',
        justifyContent: 'space-between',
      }}
    >
      <Typography variant="body2" color="text.secondary" fontWeight={500}>
        &copy; {new Date().getFullYear()} DataGate Inc. All rights reserved.
      </Typography>
      <Box sx={{ display: 'flex', gap: 3, mt: { xs: 1, sm: 0 } }}>
        <Link href="#" variant="body2" color="text.secondary" underline="hover">
          Privacy Policy
        </Link>
        <Link href="#" variant="body2" color="text.secondary" underline="hover">
          Terms of Service
        </Link>
        <Link href="#" variant="body2" color="text.secondary" underline="hover">
          Support
        </Link>
      </Box>
    </Box>
  );
};

export default Footer;