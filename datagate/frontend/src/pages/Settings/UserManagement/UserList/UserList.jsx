import React, { useState, useEffect } from 'react';
import { 
  Box, Typography, Button, Paper, Table, TableBody, 
  TableCell, TableContainer, TableHead, TableRow, 
  Chip, Avatar, CircularProgress, Dialog, DialogTitle,
  DialogContent, DialogActions, TextField, IconButton
} from '@mui/material';
import {
  PersonAdd as PersonAddIcon, 
  Edit as EditIcon,
  Shield as ShieldIcon,
} from '@mui/icons-material';
import { toast } from 'react-toastify';
import { usersApi } from '~/apis/api';

const UserList = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    full_name: '',
    password: '',
  });

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const res = await usersApi.list({ page: 1, page_size: 100 });
      setUsers(res.data || []);
    } catch {
      toast.error("Failed to fetch users. Ensure you have admin rights.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchUsers(); }, []);

  const handleSave = async () => {
    try {
      await usersApi.create(formData);
      toast.success("User created successfully!");
      setOpen(false);
      setFormData({ username: '', email: '', full_name: '', password: '' });
      fetchUsers();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to create user");
    }
  };

  return (
    <Box>
      <Box sx={{ mb: 2 }}>
        <Typography variant="caption" color="text.secondary">Settings / Users & Permissions</Typography>
      </Box>

      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h5" fontWeight="700">Team Members</Typography>
          <Typography variant="body2" color="text.secondary">Manage system access and assign roles.</Typography>
        </Box>
        <Button 
          variant="contained" 
          startIcon={<PersonAddIcon />} 
          onClick={() => setOpen(true)}
          sx={{ borderRadius: 2, textTransform: 'none' }}
        >
          Add New Member
        </Button>
      </Box>

      <TableContainer component={Paper} sx={{ borderRadius: 2, boxShadow: '0 4px 20px rgba(0,0,0,0.05)' }}>
        <Table>
          <TableHead sx={{ bgcolor: '#F8FAFC' }}>
            <TableRow>
              <TableCell sx={{ fontWeight: 700 }}>User</TableCell>
              <TableCell sx={{ fontWeight: 700 }}>Email</TableCell>
              <TableCell sx={{ fontWeight: 700 }}>Privilege</TableCell>
              <TableCell sx={{ fontWeight: 700 }}>Status</TableCell>
              <TableCell align="right" sx={{ fontWeight: 700 }}>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow><TableCell colSpan={5} align="center" sx={{ py: 5 }}><CircularProgress /></TableCell></TableRow>
            ) : users.map((user) => (
              <TableRow key={user.id} hover>
                <TableCell>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Avatar sx={{ bgcolor: user.roles?.length ? 'primary.main' : 'secondary.main', width: 32, height: 32, fontSize: '0.875rem' }}>
                      {user.full_name?.charAt(0) || 'U'}
                    </Avatar>
                    <Box>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>{user.full_name || user.username || 'Anonymous'}</Typography>
                      <Typography variant="caption" color="text.secondary">@{user.username}</Typography>
                    </Box>
                  </Box>
                </TableCell>
                <TableCell>{user.email}</TableCell>
                <TableCell>
                  {user.roles?.length ? (
                    <Chip size="small" icon={<ShieldIcon sx={{ fontSize: '0.8rem !important' }} />} label={user.roles.join(', ')} color="primary" variant="outlined" sx={{ fontWeight: 700 }} />
                  ) : (
                    <Chip size="small" label="Editor" variant="outlined" sx={{ fontWeight: 700 }} />
                  )}
                </TableCell>
                <TableCell>
                   <Chip label={user.is_active ? "Active" : "Inactive"} size="small" color={user.is_active ? "success" : "default"} sx={{ borderRadius: 1.5, fontWeight: 700 }} />
                </TableCell>
                <TableCell align="right">
                   <IconButton size="small"><EditIcon fontSize="small" /></IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Add User Dialog */}
      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="xs" fullWidth>
        <DialogTitle sx={{ fontWeight: 700 }}>Add New Team Member</DialogTitle>
        <DialogContent dividers>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2.5, pt: 1 }}>
            <TextField label="Username" fullWidth size="small" value={formData.username} onChange={(e) => setFormData({...formData, username: e.target.value})} />
            <TextField label="Full Name" fullWidth size="small" value={formData.full_name} onChange={(e) => setFormData({...formData, full_name: e.target.value})} />
            <TextField label="Email Address" fullWidth size="small" value={formData.email} onChange={(e) => setFormData({...formData, email: e.target.value})} />
            <TextField label="Initial Password" type="password" fullWidth size="small" value={formData.password} onChange={(e) => setFormData({...formData, password: e.target.value})} />
          </Box>
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleSave}>Create Account</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default UserList;
