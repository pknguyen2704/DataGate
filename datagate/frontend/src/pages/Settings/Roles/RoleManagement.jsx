import React from 'react';
import {
  Box, Typography, Paper, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Chip, IconButton, Tooltip, Stack, Button,
  Dialog, DialogTitle, DialogContent, DialogActions, TextField,
  Checkbox, FormControlLabel, Skeleton, Divider, Alert,
} from '@mui/material';
import { AddOutlined, EditOutlined, DeleteOutlined, RefreshOutlined } from '@mui/icons-material';
import { rolesApi } from '~/apis/api';

export default function RoleManagement() {
  const [roles, setRoles] = React.useState([]);
  const [permissions, setPermissions] = React.useState([]);
  const [loading, setLoading] = React.useState(true);
  const [dialogOpen, setDialogOpen] = React.useState(false);
  const [editTarget, setEditTarget] = React.useState(null);
  const [form, setForm] = React.useState({ name: '', description: '', permissionIds: [] });
  const [saving, setSaving] = React.useState(false);
  const [error, setError] = React.useState('');

  const load = React.useCallback(() => {
    setLoading(true);
    Promise.all([rolesApi.list(), rolesApi.listPermissions()])
      .then(([rRes, pRes]) => {
        setRoles(rRes.data);
        setPermissions(pRes.data);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  React.useEffect(() => { load(); }, [load]);

  const openNew = () => {
    setEditTarget(null);
    setForm({ name: '', description: '', permissionIds: [] });
    setError('');
    setDialogOpen(true);
  };

  const openEdit = (role) => {
    setEditTarget(role);
    setForm({
      name: role.name,
      description: role.description || '',
      permissionIds: role.permissions.map((p) => p.id),
    });
    setError('');
    setDialogOpen(true);
  };

  const handleSave = async () => {
    setSaving(true);
    setError('');
    try {
      if (editTarget) {
        await rolesApi.update(editTarget.id, { name: form.name, description: form.description });
        await rolesApi.assignPermissions(editTarget.id, form.permissionIds);
      } else {
        const res = await rolesApi.create({ name: form.name, description: form.description });
        if (form.permissionIds.length > 0) {
          await rolesApi.assignPermissions(res.data.id, form.permissionIds);
        }
      }
      load();
      setDialogOpen(false);
    } catch (e) {
      setError(e.response?.data?.detail || 'Save failed');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Delete this role?')) return;
    try {
      await rolesApi.delete(id);
      load();
    } catch (e) {
      alert(e.response?.data?.detail || 'Delete failed');
    }
  };

  // Group permissions by group
  const grouped = permissions.reduce((acc, p) => {
    if (!acc[p.group]) acc[p.group] = [];
    acc[p.group].push(p);
    return acc;
  }, {});

  const togglePerm = (id) => {
    setForm((f) => ({
      ...f,
      permissionIds: f.permissionIds.includes(id)
        ? f.permissionIds.filter((x) => x !== id)
        : [...f.permissionIds, id],
    }));
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h5" fontWeight={800}>Roles & Permissions</Typography>
        <Stack direction="row" spacing={1}>
          <Tooltip title="Refresh">
            <IconButton onClick={load} size="small" sx={{ border: '1px solid', borderColor: 'divider' }}>
              <RefreshOutlined fontSize="small" />
            </IconButton>
          </Tooltip>
          <Button variant="contained" startIcon={<AddOutlined />} onClick={openNew}>New Role</Button>
        </Stack>
      </Box>

      <Paper elevation={0} sx={{ border: '1px solid', borderColor: 'divider', overflow: 'hidden' }}>
        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow sx={{ bgcolor: '#F8FAFC' }}>
                {['Role Name', 'System', 'Status', 'Permissions', 'Actions'].map((h) => (
                  <TableCell key={h} sx={{ fontWeight: 700, py: 1.75 }}>{h}</TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                Array.from({ length: 4 }).map((_, i) => (
                  <TableRow key={i}>{Array.from({ length: 5 }).map((_, j) => <TableCell key={j}><Skeleton /></TableCell>)}</TableRow>
                ))
              ) : roles.map((r) => (
                <TableRow key={r.id} hover>
                  <TableCell>
                    <Typography variant="body2" fontWeight={600}>{r.name}</Typography>
                    {r.description && <Typography variant="caption" color="text.secondary">{r.description}</Typography>}
                  </TableCell>
                  <TableCell>
                    {r.is_system && <Chip label="System" size="small" color="primary" variant="outlined" />}
                  </TableCell>
                  <TableCell>
                    <Chip label={r.is_active ? 'Active' : 'Inactive'} color={r.is_active ? 'success' : 'default'} size="small" />
                  </TableCell>
                  <TableCell>
                    <Typography variant="caption" color="text.secondary">{r.permissions.length} permissions</Typography>
                  </TableCell>
                  <TableCell>
                    <Stack direction="row" spacing={0.5}>
                      <Tooltip title="Edit">
                        <IconButton size="small" onClick={() => openEdit(r)}>
                          <EditOutlined fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      {!r.is_system && (
                        <Tooltip title="Delete">
                          <IconButton size="small" color="error" onClick={() => handleDelete(r.id)}>
                            <DeleteOutlined fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      )}
                    </Stack>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* Role Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle fontWeight={700}>{editTarget ? `Edit Role: ${editTarget.name}` : 'New Role'}</DialogTitle>
        <DialogContent sx={{ pt: 2 }}>
          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
          <Stack spacing={2} mb={3}>
            <TextField
              label="Role Name"
              value={form.name}
              onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
              fullWidth
              size="small"
              disabled={editTarget?.is_system}
            />
            <TextField
              label="Description"
              value={form.description}
              onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
              fullWidth
              size="small"
            />
          </Stack>

          <Typography variant="subtitle2" fontWeight={700} mb={1.5}>Permissions</Typography>
          <Box sx={{ maxHeight: 400, overflowY: 'auto', border: '1px solid', borderColor: 'divider', borderRadius: 1, p: 2 }}>
            {Object.entries(grouped).map(([group, perms]) => (
              <Box key={group} mb={2}>
                <Typography variant="caption" fontWeight={700} color="text.secondary" sx={{ display: 'block', mb: 0.5, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                  {group}
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {perms.map((p) => (
                    <FormControlLabel
                      key={p.id}
                      control={
                        <Checkbox
                          size="small"
                          checked={form.permissionIds.includes(p.id)}
                          onChange={() => togglePerm(p.id)}
                        />
                      }
                      label={<Typography variant="caption">{p.name}</Typography>}
                      sx={{ m: 0, mr: 1 }}
                    />
                  ))}
                </Box>
                <Divider sx={{ mt: 1 }} />
              </Box>
            ))}
          </Box>
        </DialogContent>
        <DialogActions sx={{ p: 2.5, pt: 0 }}>
          <Button onClick={() => setDialogOpen(false)} color="inherit">Cancel</Button>
          <Button variant="contained" onClick={handleSave} disabled={saving}>
            {saving ? 'Saving…' : 'Save'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
