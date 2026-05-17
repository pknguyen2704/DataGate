import React, { useState } from 'react';
import { 
  Box, Button, Table, TableBody, TableCell, TableHead, TableRow, 
  Paper, Stack, IconButton, Dialog, DialogTitle, DialogContent, 
  DialogActions, TextField, Checkbox, FormControlLabel, FormGroup,
  Typography, Tooltip, Grid, Divider, Switch, Chip
} from "@mui/material";
import { 
  RefreshOutlined, EditOutlined, DeleteOutline, AddOutlined, SaveOutlined,
  ShieldOutlined, LockOutlined
} from "@mui/icons-material";
import { useSelector } from "react-redux";
import { rolesApi } from "~/apis/rolesApi";
import { StateBox, StatusChip } from "~/components/Common/DataDisplay";
import { useApiResource } from "~/hooks/useApiResource";
import { toast } from "react-toastify";

import { useConfirm } from "material-ui-confirm";

function RoleManagement() {
  const confirm = useConfirm();
  const { user: currentUser } = useSelector(state => state.auth);
  const isAdmin = currentUser?.roles?.some(r => r === "Admin" || r?.name === "Admin");
  const hasPerm = currentUser?.permissions?.some(p => p === "user:manage" || p?.code === "user:manage");
  const canManage = isAdmin || hasPerm;
  
  const roles = useApiResource(() => rolesApi.list());
  const groupedPermissions = useApiResource(() => rolesApi.listPermissionsGrouped());

  const [openRole, setOpenRole] = useState(false);
  const [editingRole, setEditingRole] = useState(null);

  const refresh = () => roles.reload();

  const handleOpenAdd = () => {
    setEditingRole(null);
    setOpenRole(true);
  };

  const handleOpenEdit = (role) => {
    setEditingRole(role);
    setOpenRole(true);
  };

  const handleDelete = (id) => {
    confirm({
      title: "Delete Role",
      description: "Are you sure you want to delete this role?",
      confirmationText: "Delete",
      cancellationText: "Cancel",
      confirmationButtonProps: { color: "error", variant: "contained" }
    })
      .then(async () => {
        try {
          await rolesApi.delete(id);
          toast.success("Role deleted");
          refresh();
        } catch (err) {
          toast.error(err.response?.data?.detail || "Failed to delete role");
        }
      })
      .catch(() => {});
  };

  const handleToggleStatus = async (role) => {
    try {
      await rolesApi.update(role.id, { is_active: !role.is_active });
      toast.success(`Role ${!role.is_active ? 'activated' : 'deactivated'}`);
      refresh();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to update status");
    }
  };

  let roleItems = [];
  if (roles.data && roles.data.items) {
    roleItems = roles.data.items;
  }

  return (
    <Box sx={{ p: 0 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3, alignItems: 'center' }}>
        <Box>
          <Typography variant="h5" fontWeight={800} color="primary">Role Management</Typography>
          <Typography variant="body2" color="text.secondary">Define access levels and group granular permissions into reusable roles.</Typography>
        </Box>
        <Stack direction="row" spacing={1}>
          <Button startIcon={<RefreshOutlined />} variant="outlined" onClick={refresh}>
            Refresh
          </Button>
          {canManage && (
            <Button startIcon={<AddOutlined />} variant="contained" onClick={handleOpenAdd}>
              New Role
            </Button>
          )}
        </Stack>
      </Box>

      <StateBox loading={roles.loading} error={roles.error} empty={roleItems.length === 0}>
        <Paper variant="outlined" sx={{ borderRadius: 2, overflow: 'hidden' }}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Role Name</TableCell>
                <TableCell>Description</TableCell>
                <TableCell>Permissions</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {roleItems.map((role) => (
                <TableRow key={role.id} hover>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                      <Box sx={{ p: 1, bgcolor: 'primary.50', color: 'primary.main', borderRadius: 1 }}>
                        <ShieldOutlined fontSize="small" />
                      </Box>
                      <Typography variant="body2" fontWeight={700}>{role.name}</Typography>
                      {role.is_system && (
                        <Tooltip title="System Role">
                          <LockOutlined sx={{ fontSize: 14, color: 'text.disabled' }} />
                        </Tooltip>
                      )}
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Typography variant="caption" color="text.secondary">{role.description || "—"}</Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" fontWeight={700} color="secondary.main">
                      {(role.permissions || []).length} permissions
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Switch 
                        size="small" 
                        checked={role.is_active} 
                        onChange={() => handleToggleStatus(role)}
                        color="success"
                        disabled={!canManage || role.is_system}
                      />
                      <Chip 
                        label={role.is_active ? "Active" : "Inactive"} 
                        size="small" 
                        variant="outlined" 
                        color={role.is_active ? "success" : "default"}
                        sx={{ ml: 1, border: 'none', fontWeight: 600 }}
                      />
                    </Box>
                  </TableCell>
                  <TableCell align="right">
                    <Stack direction="row" spacing={0.5} justifyContent="flex-end">
                      {canManage && (
                        <>
                          <Tooltip title="Edit Role">
                            <IconButton size="small" color="primary" onClick={() => handleOpenEdit(role)}>
                              <EditOutlined fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title={role.is_system ? "System roles cannot be deleted" : "Delete Role"}>
                            <span>
                              <IconButton size="small" color="error" onClick={() => handleDelete(role.id)} disabled={role.is_system}>
                                <DeleteOutline fontSize="small" />
                              </IconButton>
                            </span>
                          </Tooltip>
                        </>
                      )}
                    </Stack>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Paper>
      </StateBox>

      {/* Role Dialog */}
      <RoleDialog 
        open={openRole} 
        onClose={() => setOpenRole(false)} 
        role={editingRole} 
        groupedPermissions={groupedPermissions.data || {}}
        onSuccess={refresh}
      />
    </Box>
  );
}

function RoleDialog({ open, onClose, role, groupedPermissions, onSuccess }) {
  const [form, setForm] = useState({ name: "", description: "", permission_ids: [] });
  const [saving, setSaving] = useState(false);

  React.useEffect(() => {
    if (role) {
      setForm({
        name: role.name,
        description: role.description || "",
        permission_ids: (role.permissions || []).map(p => p.id)
      });
    } else {
      setForm({ name: "", description: "", permission_ids: [] });
    }
  }, [role, open]);

  const handleSave = async () => {
    setSaving(true);
    try {
      if (role) {
        await rolesApi.update(role.id, {
          name: form.name,
          description: form.description,
          permission_ids: form.permission_ids
        });
        toast.success("Role updated");
      } else {
        await rolesApi.create(form);
        toast.success("Role created");
      }
      onSuccess();
      onClose();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to save role");
    } finally {
      setSaving(false);
    }
  };

  const togglePermission = (id) => {
    setForm(prev => {
      const exists = prev.permission_ids.includes(id);
      return {
        ...prev,
        permission_ids: exists 
          ? prev.permission_ids.filter(pid => pid !== id)
          : [...prev.permission_ids, id]
      };
    });
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle sx={{ fontWeight: 700 }}>{role ? "Edit Role" : "Create New Role"}</DialogTitle>
      <DialogContent dividers>
        <Stack spacing={2} sx={{ mt: 1 }}>
          <Stack direction="row" spacing={2}>
            <TextField 
              label="Role Name" 
              fullWidth 
              size="small" 
              value={form.name} 
              onChange={e => setForm({...form, name: e.target.value})} 
              disabled={role?.is_system}
            />
            <TextField 
              label="Description" 
              fullWidth 
              size="small" 
              value={form.description} 
              onChange={e => setForm({...form, description: e.target.value})} 
            />
          </Stack>

          <Box>
            <Typography variant="subtitle1" sx={{ mb: 1, fontWeight: 700, color: 'primary.main' }}>Permissions</Typography>
            <Grid container spacing={2}>
              {Object.entries(groupedPermissions).map(([group, perms]) => (
                <Grid item xs={12} md={6} key={group}>
                  <Paper variant="outlined" sx={{ p: 2, borderRadius: 2, height: '100%', bgcolor: '#f8fafc' }}>
                    <Typography variant="caption" fontWeight={800} color="text.secondary" sx={{ textTransform: 'uppercase', mb: 1, display: 'block' }}>
                      {group}
                    </Typography>
                    <Divider sx={{ mb: 1.5 }} />
                    <FormGroup>
                      {perms.map(p => (
                        <FormControlLabel 
                          key={p.id}
                          control={
                            <Checkbox 
                              size="small"
                              checked={form.permission_ids.includes(p.id)} 
                              onChange={() => togglePermission(p.id)}
                            />
                          }
                          label={<Typography variant="body2">{p.name}</Typography>}
                        />
                      ))}
                    </FormGroup>
                  </Paper>
                </Grid>
              ))}
            </Grid>
          </Box>
        </Stack>
      </DialogContent>
      <DialogActions sx={{ p: 2 }}>
        <Button onClick={onClose}>Cancel</Button>
        <Button variant="contained" startIcon={<SaveOutlined />} onClick={handleSave} disabled={saving}>
          {saving ? "Saving..." : "Save Role"}
        </Button>
      </DialogActions>
    </Dialog>
  );
}

export default RoleManagement;
