import React from 'react';
import { Box, Typography, Button } from '@mui/material';
import { HomeOutlined } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

export default function NotFound() {
  const navigate = useNavigate();
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        textAlign: 'center',
        gap: 3,
        px: 2,
      }}
    >
      <Typography variant="h1" fontWeight={900} sx={{ fontSize: '6rem', color: 'divider', lineHeight: 1 }}>
        404
      </Typography>
      <Typography variant="h5" fontWeight={700}>Page not found</Typography>
      <Typography variant="body1" color="text.secondary">
        The page you're looking for doesn't exist or has been moved.
      </Typography>
      <Button variant="contained" startIcon={<HomeOutlined />} onClick={() => navigate('/home')}>
        Back to Home
      </Button>
    </Box>
  );
}