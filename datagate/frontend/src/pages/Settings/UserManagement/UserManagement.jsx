import React, { useState } from 'react';
import { 
  Box, Button, Table, TableBody, TableCell, TableHead, TableRow, 
  Paper, Stack, IconButton, Dialog, DialogTitle, DialogContent, 
  DialogActions, TextField, Checkbox, FormControlLabel, FormGroup,
  Typography, Tooltip, MenuItem, Select, FormControl, InputLabel,
  TablePagination, TableContainer, Switch, Chip
} from "@mui/material";
import { 
  RefreshOutlined, EditOutlined, AddOutlined, SaveOutlined, 
  LockOpenOutlined, PersonOffOutlined, PersonOutline, KeyOutlined
} from "@mui/icons-material";
import { useSelector } from "react-redux";
import { usersApi } from "~/apis/usersApi";
import { rolesApi } from "~/apis/rolesApi";
import { StateBox, StatusChip } from "~/components/Common/DataDisplay";
import { useApiResource } from "~/hooks/useApiResource";
import { toast } from "react-toastify";

function UserManagement() {
  const { user: currentUser } = useSelector(state => state.auth);
  const isAdmin = currentUser?.roles?.some(r => r === "Admin" || r?.name === "Admin");
  const hasPerm = currentUser?.permissions?.some(p => p === "user:manage" || p?.code === "user:manage");
  const canManage = isAdmin || hasPerm;
  
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  
  const users = useApiResource(() => usersApi.list({ 
    page: page + 1, 
    page_size: pageSize 
  }), [page, pageSize]);
  
  const roles = useApiResource(() => rolesApi.list());

  const [openUser, setOpenUser] = useState(false);
  const [openPassword, setOpenPassword] = useState(false);
  const [editingUser, setEditingUser] = useState(null);

  const refresh = () => users.reload();

  const handleOpenAdd = () => {
    setEditingUser(null);
    setOpenUser(true);
  };

  const handleOpenEdit = (user) => {
    setEditingUser(user);
    setOpenUser(true);
  };

  const handleOpenPassword = (user) => {
    setEditingUser(user);
    setOpenPassword(true);
  };

  const handleToggleStatus = async (user) => {
    try {
      if (user.is_active) {
        await usersApi.deactivate(user.id);
        toast.success("User deactivated");
      } else {
        await usersApi.activate(user.id);
        toast.success("User activated");
      }
      refresh();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to update status");
    }
  };

  let userItems = [];
  if (users.data && users.data.items) {
    userItems = users.data.items;
  }

  return (
    <Box sx={{ p: 0 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3, alignItems: 'center' }}>
        <Box>
          <Typography variant="h5" fontWeight={800} color="primary">User Management</Typography>
          <Typography variant="body2" color="text.secondary">Create and manage system users and their access roles.</Typography>
        </Box>
        <Stack direction="row" spacing={1}>
          <Button startIcon={<RefreshOutlined />} variant="outlined" onClick={refresh}>
            Refresh
          </Button>
          {canManage && (
            <Button startIcon={<AddOutlined />} variant="contained" onClick={handleOpenAdd}>
              New User
            </Button>
          )}
        </Stack>
      </Box>

      <StateBox loading={users.loading} error={users.error} empty={userItems.length === 0}>
        <TableContainer component={Paper} variant="outlined" sx={{ borderRadius: 2, overflow: 'hidden' }}>
          <Table size="small">
            <TableHead>
              <TableRow sx={{ bgcolor: 'primary.light', '& .MuiTableCell-head': { fontWeight: 700 } }}>
                <TableCell>User</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Roles</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {userItems.map((user) => (
                <TableRow key={user.id} hover>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                      <Box sx={{ p: 1, bgcolor: 'grey.100', borderRadius: 1 }}>
                        <PersonOutline fontSize="small" />
                      </Box>
                      <Box>
                        <Typography variant="body2" fontWeight={700}>{user.username}</Typography>
                        <Typography variant="caption" color="text.secondary">{user.full_name || "No name provided"}</Typography>
                      </Box>
                    </Box>
                  </TableCell>
                  <TableCell>{user.email}</TableCell>
                  <TableCell>
                    <Stack direction="row" spacing={0.5} flexWrap="wrap">
                      {(user.roles || []).map((r) => (
                        <Typography key={r.id} variant="caption" sx={{ bgcolor: 'primary.50', color: 'primary.main', px: 1, py: 0.2, borderRadius: 1, fontWeight: 700 }}>
                          {r.name}
                        </Typography>
                      ))}
                    </Stack>
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Switch 
                        size="small" 
                        checked={user.is_active} 
                        onChange={() => handleToggleStatus(user)}
                        color="success"
                        disabled={!canManage || user.id === currentUser?.id}
                      />
                      <Chip 
                        label={user.is_active ? "Active" : "Inactive"} 
                        size="small" 
                        variant="outlined" 
                        color={user.is_active ? "success" : "default"}
                        sx={{ ml: 1, border: 'none', fontWeight: 600 }}
                      />
                    </Box>
                  </TableCell>
                  <TableCell align="right">
                    <Stack direction="row" spacing={0.5} justifyContent="flex-end">
                      {canManage && (
                        <>
                          <Tooltip title="Edit User">
                            <IconButton size="small" color="primary" onClick={() => handleOpenEdit(user)}>
                              <EditOutlined fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Reset Password">
                            <IconButton size="small" color="secondary" onClick={() => handleOpenPassword(user)}>
                              <KeyOutlined fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </>
                      )}
                    </Stack>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          <TablePagination
            rowsPerPageOptions={[5, 10, 25]}
            component="div"
            count={users.data?.total || 0}
            rowsPerPage={pageSize}
            page={page}
            onPageChange={(e, newPage) => setPage(newPage)}
            onRowsPerPageChange={(e) => {
              setPageSize(parseInt(e.target.value, 10));
              setPage(0);
            }}
          />
        </TableContainer>
      </StateBox>

      {/* User Dialog */}
      <UserDialog 
        open={openUser} 
        onClose={() => setOpenUser(false)} 
        user={editingUser} 
        roles={roles.data?.items || []}
        onSuccess={refresh}
      />

      {/* Password Dialog */}
      <PasswordDialog 
        open={openPassword} 
        onClose={() => setOpenPassword(false)} 
        user={editingUser} 
      />
    </Box>
  );
}

function UserDialog({ open, onClose, user, roles, onSuccess }) {
  const [form, setForm] = useState({ username: "", full_name: "", email: "", password: "", role_ids: [] });
  const [saving, setSaving] = useState(false);

  React.useEffect(() => {
    if (user) {
      setForm({
        username: user.username,
        full_name: user.full_name || "",
        email: user.email,
        password: "",
        role_ids: (user.roles || []).map(r => r.id)
      });
    } else {
      setForm({ username: "", full_name: "", email: "", password: "", role_ids: [] });
    }
  }, [user, open]);

  const handleSave = async () => {
    setSaving(true);
    try {
      if (user) {
        await usersApi.update(user.id, {
          username: form.username,
          full_name: form.full_name,
          email: form.email,
          role_ids: form.role_ids
        });
        toast.success("User updated");
      } else {
        await usersApi.create(form);
        toast.success("User created");
      }
      onSuccess();
      onClose();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to save user");
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle sx={{ fontWeight: 700 }}>{user ? "Edit User" : "Create New User"}</DialogTitle>
      <DialogContent dividers>
        <Stack spacing={2} sx={{ mt: 1 }}>
          <TextField label="Username" fullWidth size="small" value={form.username} onChange={e => setForm({...form, username: e.target.value})} disabled={!!user} />
          <TextField label="Full Name" fullWidth size="small" value={form.full_name} onChange={e => setForm({...form, full_name: e.target.value})} />
          <TextField label="Email" fullWidth size="small" value={form.email} onChange={e => setForm({...form, email: e.target.value})} />
          {!user && <TextField label="Password" type="password" fullWidth size="small" value={form.password} onChange={e => setForm({...form, password: e.target.value})} />}
          
          <Box>
            <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 700 }}>Roles</Typography>
            <Paper variant="outlined" sx={{ p: 1, bgcolor: '#f8fafc' }}>
              <FormGroup row>
                {roles.map(r => (
                  <FormControlLabel 
                    key={r.id}
                    control={
                      <Checkbox 
                        size="small"
                        checked={form.role_ids.includes(r.id)} 
                        onChange={e => {
                          const newIds = e.target.checked ? [...form.role_ids, r.id] : form.role_ids.filter(id => id !== r.id);
                          setForm({...form, role_ids: newIds});
                        }}
                      />
                    }
                    label={<Typography variant="body2">{r.name}</Typography>}
                  />
                ))}
              </FormGroup>
            </Paper>
          </Box>
        </Stack>
      </DialogContent>
      <DialogActions sx={{ p: 2 }}>
        <Button onClick={onClose}>Cancel</Button>
        <Button variant="contained" startIcon={<SaveOutlined />} onClick={handleSave} disabled={saving}>
          {saving ? "Saving..." : "Save User"}
        </Button>
      </DialogActions>
    </Dialog>
  );
}

function PasswordDialog({ open, onClose, user }) {
  const [password, setPassword] = useState("");
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    if (!password) return toast.warning("Password cannot be empty");
    setSaving(true);
    try {
      await usersApi.updatePassword(user.id, password);
      toast.success("Password reset successfully");
      onClose();
      setPassword("");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to reset password");
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="xs" fullWidth>
      <DialogTitle sx={{ fontWeight: 700 }}>Reset Password</DialogTitle>
      <DialogContent dividers>
        <Typography variant="body2" sx={{ mb: 2 }}>
          Set a new password for user: <strong>{user?.username}</strong>
        </Typography>
        <TextField 
          label="New Password" 
          type="password" 
          fullWidth 
          size="small" 
          value={password} 
          onChange={e => setPassword(e.target.value)}
          autoFocus
        />
      </DialogContent>
      <DialogActions sx={{ p: 2 }}>
        <Button onClick={onClose}>Cancel</Button>
        <Button variant="contained" color="secondary" startIcon={<SaveOutlined />} onClick={handleSave} disabled={saving}>
          {saving ? "Resetting..." : "Reset Password"}
        </Button>
      </DialogActions>
    </Dialog>
  );
}

export default UserManagement;
