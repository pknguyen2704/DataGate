import React from 'react';
import { Box, Typography, Button, Container } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';

const NotFound = () => {
  const navigate = useNavigate();

  return (
    <Container maxWidth="md">
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '80vh',
          textAlign: 'center',
          gap: 3,
        }}
      >
        <ErrorOutlineIcon sx={{ fontSize: 100, color: 'text.secondary', opacity: 0.5 }} />
        
        <Typography variant="h1" fontWeight="bold" color="primary.main">
          404
        </Typography>
        
        <Typography variant="h4" color="text.primary" fontWeight={600}>
          Page not found
        </Typography>
        
        <Typography variant="body1" color="text.secondary" sx={{ maxWidth: 500, mb: 2 }}>
          Oops! The page you are looking for might have been moved, renamed, or never existed in the DataGate system.
        </Typography>

        <Button
          variant="contained"
          color="primary"
          size="large"
          onClick={() => navigate('/')}
          sx={{ borderRadius: 2, px: 4, py: 1.5, textTransform: 'none', fontWeight: 'bold' }}
        >
          Back to Home
        </Button>
      </Box>
    </Container>
  );
};

export default NotFound;