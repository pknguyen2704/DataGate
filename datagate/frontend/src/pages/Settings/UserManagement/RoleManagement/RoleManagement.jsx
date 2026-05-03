import React, { useState, useEffect } from 'react';
import { 
  Box, Typography, Button, Paper, Table, TableBody, 
  TableCell, TableContainer, TableHead, TableRow, 
  Chip, CircularProgress, Dialog, DialogTitle,
  DialogContent, DialogActions, TextField, IconButton,
  Checkbox, FormControlLabel, FormGroup, Divider, Grid
} from '@mui/material';
import {
  Add as AddIcon, 
  Edit as EditIcon,
  Shield as ShieldIcon,
  Delete as DeleteIcon,
  Lock as LockIcon
} from '@mui/icons-material';
import { useConfirm } from 'material-ui-confirm';
import { toast } from 'react-toastify';
import { rolesApi } from '../../../../apis/api';

const RoleManagement = () => {
  const confirm = useConfirm();
  const [roles, setRoles] = useState([]);
  const [permissions, setPermissions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const [editingRole, setEditingRole] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    is_active: true
  });
  const [selectedPerms, setSelectedPerms] = useState([]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [rolesRes, permsRes] = await Promise.all([
        rolesApi.list(),
        rolesApi.listPermissions()
      ]);
      setRoles(rolesRes.data);
      setPermissions(permsRes.data);
    } catch {
      toast.error("Failed to fetch roles or permissions");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  const handleOpen = (role = null) => {
    if (role) {
      setEditingRole(role);
      setFormData({
        name: role.name,
        description: role.description || '',
        is_active: role.is_active
      });
      setSelectedPerms(role.permissions.map(p => p.id));
    } else {
      setEditingRole(null);
      setFormData({ name: '', description: '', is_active: true });
      setSelectedPerms([]);
    }
    setOpen(true);
  };

  const handleSave = async () => {
    if (!formData.name) {
      toast.error("Role name is required");
      return;
    }
    try {
      let roleId;
      if (editingRole) {
        await rolesApi.update(editingRole.id, formData);
        roleId = editingRole.id;
        toast.success("Role updated successfully");
      } else {
        const res = await rolesApi.create(formData);
        roleId = res.data.id;
        toast.success("Role created successfully");
      }
      
      // Update permissions
      await rolesApi.assignPermissions(roleId, selectedPerms);
      
      setOpen(false);
      fetchData();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to save role");
    }
  };

  const handleDelete = async (id) => {
    try {
      await confirm({
        title: 'Delete role?',
        description: 'Are you sure you want to delete this role?',
        confirmationText: 'Delete',
        cancellationText: 'Cancel',
        confirmationButtonProps: {
          color: 'error',
          variant: 'contained',
        },
      });
    } catch {
      return;
    }

    try {
      await rolesApi.delete(id);
      toast.success("Role deleted successfully");
      fetchData();
    } catch {
      toast.error("Failed to delete role");
    }
  };

  const togglePerm = (permId) => {
    setSelectedPerms(prev => 
      prev.includes(permId) ? prev.filter(id => id !== permId) : [...prev, permId]
    );
  };

  // Group permissions by group field
  const permsByGroup = permissions.reduce((acc, p) => {
    const group = p.group || 'Other';
    if (!acc[group]) acc[group] = [];
    acc[group].push(p);
    return acc;
  }, {});

  return (
    <Box>
      <Box sx={{ mb: 2 }}>
        <Typography variant="caption" color="text.secondary">Settings / Roles & Permissions</Typography>
      </Box>

      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h5" fontWeight="700">Security Roles</Typography>
          <Typography variant="body2" color="text.secondary">Define access levels and assign granular permissions.</Typography>
        </Box>
        <Button 
          variant="contained" 
          startIcon={<AddIcon />} 
          onClick={() => handleOpen()}
          sx={{ borderRadius: 2, textTransform: 'none', fontWeight: 700 }}
        >
          Create New Role
        </Button>
      </Box>

      <TableContainer component={Paper} sx={{ borderRadius: 2, boxShadow: '0 4px 20px rgba(0,0,0,0.05)' }}>
        <Table>
          <TableHead sx={{ bgcolor: '#F8FAFC' }}>
            <TableRow>
              <TableCell sx={{ fontWeight: 700 }}>Role Name</TableCell>
              <TableCell sx={{ fontWeight: 700 }}>Description</TableCell>
              <TableCell sx={{ fontWeight: 700 }}>Permissions</TableCell>
              <TableCell sx={{ fontWeight: 700 }}>Status</TableCell>
              <TableCell align="right" sx={{ fontWeight: 700 }}>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow><TableCell colSpan={5} align="center" sx={{ py: 5 }}><CircularProgress /></TableCell></TableRow>
            ) : roles.map((role) => (
              <TableRow key={role.id} hover>
                <TableCell>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                    <ShieldIcon color={role.is_system ? "primary" : "secondary"} fontSize="small" />
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>{role.name}</Typography>
                    {role.is_system && <Chip label="System" size="small" variant="outlined" sx={{ height: 20, fontSize: '0.65rem' }} />}
                  </Box>
                </TableCell>
                <TableCell>
                  <Typography variant="caption" color="text.secondary">{role.description || '-'}</Typography>
                </TableCell>
                <TableCell>
                  <Typography variant="body2" fontWeight={700} color="primary">
                    {role.permissions?.length || 0} enabled
                  </Typography>
                </TableCell>
                <TableCell>
                   <Chip label={role.is_active ? "Active" : "Inactive"} size="small" color={role.is_active ? "success" : "default"} sx={{ borderRadius: 1.5, fontWeight: 700 }} />
                </TableCell>
                <TableCell align="right">
                   <IconButton size="small" onClick={() => handleOpen(role)}><EditIcon fontSize="small" /></IconButton>
                   <IconButton 
                    size="small" 
                    color="error" 
                    disabled={role.is_system}
                    onClick={() => handleDelete(role.id)}
                   >
                    {role.is_system ? <LockIcon fontSize="small" /> : <DeleteIcon fontSize="small" />}
                   </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Role Editor Dialog */}
      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle sx={{ fontWeight: 700 }}>
          {editingRole ? `Edit Role: ${editingRole.name}` : 'Create New Security Role'}
        </DialogTitle>
        <DialogContent dividers>
          <Grid container spacing={4}>
            <Grid item xs={12} md={4}>
              <Stack spacing={2.5}>
                <Typography variant="subtitle2" fontWeight={800}>General Details</Typography>
                <TextField label="Role Name" fullWidth size="small" value={formData.name} onChange={(e) => setFormData({...formData, name: e.target.value})} disabled={editingRole?.is_system} />
                <TextField label="Description" fullWidth size="small" multiline rows={3} value={formData.description} onChange={(e) => setFormData({...formData, description: e.target.value})} />
                <FormControlLabel 
                  control={<Checkbox checked={formData.is_active} onChange={(e) => setFormData({...formData, is_active: e.target.checked})} />} 
                  label="Role is Active" 
                />
              </Stack>
            </Grid>
            <Grid item xs={12} md={8}>
              <Typography variant="subtitle2" fontWeight={800} mb={2}>Permissions Matrix</Typography>
              <Box sx={{ maxHeight: 400, overflow: 'auto', pr: 1 }}>
                {Object.entries(permsByGroup).map(([group, groupPerms]) => (
                  <Box key={group} sx={{ mb: 3 }}>
                    <Typography variant="caption" fontWeight={900} color="primary" sx={{ textTransform: 'uppercase', letterSpacing: 1 }}>
                      {group}
                    </Typography>
                    <Divider sx={{ my: 1 }} />
                    <FormGroup row>
                      {groupPerms.map(p => (
                        <FormControlLabel 
                          key={p.id}
                          sx={{ width: '50%', m: 0 }}
                          control={
                            <Checkbox 
                              size="small" 
                              checked={selectedPerms.includes(p.id)} 
                              onChange={() => togglePerm(p.id)} 
                            />
                          } 
                          label={<Typography variant="caption">{p.name}</Typography>} 
                        />
                      ))}
                    </FormGroup>
                  </Box>
                ))}
              </Box>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleSave} sx={{ fontWeight: 700 }}>
            {editingRole ? 'Save Changes' : 'Create Role'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default RoleManagement;
