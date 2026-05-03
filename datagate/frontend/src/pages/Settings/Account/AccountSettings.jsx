import React, { useState, useEffect } from 'react';
import { 
  Box, Typography, Button, Paper, TextField, Stack,
  Avatar, Chip, Grid, CircularProgress
} from '@mui/material';
import {
  Save as SaveIcon,
  Email as EmailIcon,
  Person as PersonIcon,
  Key as KeyIcon
} from '@mui/icons-material';
import { toast } from 'react-toastify';
import { usersApi } from '~/apis/api';

const AccountSettings = () => {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [user, setUser] = useState({
    email: '',
    full_name: '',
  });
  const [passwords, setPasswords] = useState({
    new: '',
    confirm: ''
  });

  useEffect(() => {
    const fetchMe = async () => {
      try {
        const res = await usersApi.getMe();
        setUser(res.data);
      } catch {
        toast.error("Failed to load profile");
      } finally {
        setLoading(false);
      }
    };
    fetchMe();
  }, []);

  const handleUpdateProfile = async () => {
    setSaving(true);
    try {
      await usersApi.updateMe({ full_name: user.full_name });
      toast.success("Profile updated successfully");
    } catch {
      toast.error("Failed to update profile");
    } finally {
      setSaving(false);
    }
  };

  const handleUpdatePassword = async () => {
    if (passwords.new !== passwords.confirm) {
      toast.error("New passwords do not match");
      return;
    }
    setSaving(true);
    try {
      await usersApi.updateMe({ password: passwords.new });
      toast.success("Password changed successfully");
      setPasswords({ new: '', confirm: '' });
    } catch {
      toast.error("Failed to change password");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <Box sx={{ display: 'flex', justifyContent: 'center', p: 10 }}><CircularProgress /></Box>;
  }

  return (
    <Box sx={{ maxWidth: 800 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h5" fontWeight="800" mb={1}>Account Settings</Typography>
        <Typography variant="body2" color="text.secondary">
          Manage your personal profile and security preferences.
        </Typography>
      </Box>

      <Grid container spacing={4}>
        <Grid item xs={12} md={4}>
          <Paper className="glass-card" elevation={0} sx={{ p: 4, textAlign: 'center', borderRadius: 2 }}>
            <Avatar 
              sx={{ 
                width: 100, 
                height: 100, 
                mx: 'auto', 
                mb: 2, 
                bgcolor: 'primary.main',
                fontSize: '2rem'
              }}
            >
              {user.full_name?.charAt(0) || <PersonIcon fontSize="large" />}
            </Avatar>
            <Typography variant="h6" fontWeight={700}>{user.full_name}</Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>{user.email}</Typography>
            <Chip label="Administrator" size="small" sx={{ mt: 1, fontWeight: 700 }} />
          </Paper>
        </Grid>

        <Grid item xs={12} md={8}>
          <Stack spacing={4}>
            {/* PROFILE SECTION */}
            <Paper className="glass-card" elevation={0} sx={{ p: 4, borderRadius: 2 }}>
              <Typography variant="subtitle1" fontWeight={800} mb={3} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <PersonIcon color="primary" /> Profile Information
              </Typography>
              <Stack spacing={3}>
                <TextField 
                  fullWidth label="Full Name" value={user.full_name} 
                  onChange={(e) => setUser({...user, full_name: e.target.value})}
                  size="small"
                />
                <TextField 
                  fullWidth label="Email Address" value={user.email} 
                  disabled 
                  size="small"
                  InputProps={{
                    startAdornment: <EmailIcon sx={{ mr: 1, color: 'text.secondary', fontSize: 18 }} />
                  }}
                />
                <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                  <Button 
                    variant="contained" 
                    startIcon={<SaveIcon />} 
                    disabled={saving}
                    onClick={handleUpdateProfile}
                    sx={{ borderRadius: 2, fontWeight: 700 }}
                  >
                    Update Profile
                  </Button>
                </Box>
              </Stack>
            </Paper>

            {/* SECURITY SECTION */}
            <Paper className="glass-card" elevation={0} sx={{ p: 4, borderRadius: 2 }}>
              <Typography variant="subtitle1" fontWeight={800} mb={3} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <KeyIcon color="warning" /> Security & Password
              </Typography>
              <Stack spacing={2.5}>
                <TextField 
                  fullWidth label="New Password" type="password" 
                  value={passwords.new} onChange={(e) => setPasswords({...passwords, new: e.target.value})}
                  size="small"
                />
                <TextField 
                  fullWidth label="Confirm New Password" type="password" 
                  value={passwords.confirm} onChange={(e) => setPasswords({...passwords, confirm: e.target.value})}
                  size="small"
                />
                <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                  <Button 
                    variant="outlined" 
                    color="warning"
                    disabled={saving || !passwords.new}
                    onClick={handleUpdatePassword}
                    sx={{ borderRadius: 2, fontWeight: 700 }}
                  >
                    Change Password
                  </Button>
                </Box>
              </Stack>
            </Paper>
          </Stack>
        </Grid>
      </Grid>
    </Box>
  );
};

export default AccountSettings;
