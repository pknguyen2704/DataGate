import React, { useState } from 'react';
import { 
  Box, Typography, TextField, Button, Paper, 
  Divider, Alert
} from '@mui/material';
import { Lock as LockIcon, Save as SaveIcon } from '@mui/icons-material';
import { toast } from 'react-toastify';
import { usersApi } from '../../../apis/users';

const PasswordChange = () => {
  const [formData, setFormData] = useState({
    password: '',
    confirmPassword: ''
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (formData.password !== formData.confirmPassword) {
      toast.error("Passwords do not match");
      return;
    }
    
    setLoading(true);
    try {
      await usersApi.updateMe({ password: formData.password });
      toast.success("Security settings updated successfully!");
      setFormData({ password: '', confirmPassword: '' });
    } catch (err) {
      toast.error(err.response?.data?.detail || "Update failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box maxWidth="sm">
      <Box sx={{ mb: 2 }}>
        <Typography variant="caption" color="text.secondary">Settings / Security</Typography>
      </Box>

      <Box sx={{ mb: 4 }}>
        <Typography variant="h5" fontWeight="700">Security Settings</Typography>
        <Typography variant="body2" color="text.secondary">Manage your password and account protection.</Typography>
      </Box>

      <Paper sx={{ p: 4, borderRadius: 2, boxShadow: '0 4px 20px rgba(0,0,0,0.05)' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 3 }}>
           <Box sx={{ bgcolor: 'secondary.light', p: 1, borderRadius: 1.5, display: 'flex' }}>
             <LockIcon color="secondary" />
           </Box>
           <Typography variant="h6" fontWeight="600">Change Password</Typography>
        </Box>
        
        <Alert severity="info" sx={{ mb: 3 }}>
          Ensure your new password contains at least 8 characters including numbers and special characters.
        </Alert>

        <form onSubmit={handleSubmit}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            <TextField
              label="New Password"
              type="password"
              fullWidth
              required
              value={formData.password}
              onChange={(e) => setFormData({...formData, password: e.target.value})}
            />
            <TextField
              label="Confirm New Password"
              type="password"
              fullWidth
              required
              value={formData.confirmPassword}
              onChange={(e) => setFormData({...formData, confirmPassword: e.target.value})}
            />
            
            <Divider />
            
            <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
              <Button 
                type="submit" 
                variant="contained" 
                disabled={loading}
                startIcon={<SaveIcon />}
                sx={{ borderRadius: 2, px: 4, py: 1 }}
              >
                Update Password
              </Button>
            </Box>
          </Box>
        </form>
      </Paper>
    </Box>
  );
};

export default PasswordChange;
