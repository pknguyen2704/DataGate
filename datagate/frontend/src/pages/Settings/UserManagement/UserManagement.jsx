import React, { useState } from 'react';
import {
  Box, Button, Table, TableBody, TableCell, TableHead, TableRow,
  Paper, Stack, IconButton, Dialog, DialogTitle, DialogContent,
  DialogActions, TextField,
  Typography, Tooltip, MenuItem, Select, FormControl, InputLabel,
  TablePagination, TableContainer, Grid
} from "@mui/material";
import {
  EditOutlined, AddOutlined, SaveOutlined,
  PersonOutline, VisibilityOutlined, ArrowBackOutlined, DeleteOutline
} from "@mui/icons-material";
import { useRBAC } from "~/rbac/useRBAC";
import { PermissionCode } from "~/rbac/permission";
import { usersApi } from "~/apis/usersApi";
import { rolesApi } from "~/apis/rolesApi";
import { StateBox, StatusChip } from "~/components/Common/DataDisplay";
import { useApiResource } from "~/hooks/useApiResource";
import { toast } from "react-toastify";
import { useConfirm } from "material-ui-confirm";

function UserManagement() {
  const { hasPermission } = useRBAC();
  const canManage = hasPermission(PermissionCode.USER_MANAGE);

  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const [selectedId, setSelectedId] = useState(null);

  const users = useApiResource(() => usersApi.list({
    page: page + 1,
    page_size: pageSize
  }), [page, pageSize]);

  const roles = useApiResource(() => rolesApi.list());
  const confirm = useConfirm();

  const [openUser, setOpenUser] = useState(false);
  const [editingUser, setEditingUser] = useState(null);

  const handleOpenAdd = () => {
    setEditingUser(null);
    setOpenUser(true);
  };

  const handleOpenEdit = (user) => {
    setEditingUser(user);
    setOpenUser(true);
  };

  const handleDelete = (id) => {
    confirm({
      title: "Delete User",
      description: "Are you sure you want to permanently delete this user?",
      confirmationText: "Delete",
      cancellationText: "Cancel",
      confirmationButtonProps: { color: "error", variant: "contained" }
    })
      .then(async () => {
        try {
          await usersApi.delete(id);
          toast.success("User deleted successfully");
          setSelectedId(null);
          users.reload();
        } catch (error) {
          console.error(error);
          toast.error(error.response?.data?.detail || "Failed to delete user");
        }
      })
      .catch(() => { });
  };

  let userItems = [];
  if (users.data && users.data.items) {
    userItems = users.data.items;
  }

  const selectedUser = userItems.find(u => u.id === selectedId);

  const userDialog = (
    <UserDialog
      open={openUser}
      onClose={() => {
        setOpenUser(false);
        if (selectedId) {
          users.reload();
        }
      }}
      user={editingUser}
      roles={roles.data?.items || []}
      onSuccess={() => users.reload()}
    />
  );

  if (selectedUser) {
    return (
      <Box sx={{ p: 0, pt: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <IconButton onClick={() => setSelectedId(null)} sx={{ mr: 1 }} color="primary">
            <ArrowBackOutlined />
          </IconButton>
          <Typography variant="h6" fontWeight={700}>User Details</Typography>
        </Box>

        <Paper variant="outlined" sx={{ p: 3, borderRadius: 2 }}>
          <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 3, pb: 2, borderBottom: 1, borderColor: 'divider' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Box sx={{ p: 2, bgcolor: 'grey.100', borderRadius: 2 }}>
                <PersonOutline sx={{ fontSize: 40 }} />
              </Box>
              <Box>
                <Typography variant="caption" color="text.secondary" fontWeight={700}>USERNAME</Typography>
                <Typography variant="h6" fontWeight={800}>
                  {selectedUser.username}
                </Typography>
              </Box>
            </Box>
            <Stack direction="row" spacing={1}>
              {canManage && (
                <>
                  <Button size="small" variant="outlined" startIcon={<EditOutlined />} onClick={() => handleOpenEdit(selectedUser)}>
                    Edit
                  </Button>
                  <Button size="small" variant="outlined" color="error" startIcon={<DeleteOutline />} onClick={() => handleDelete(selectedUser.id)}>
                    Delete
                  </Button>
                </>
              )}
            </Stack>
          </Stack>

          <Grid container spacing={3}>
            <Grid item xs={12} sm={6} md={4}>
              <Paper variant="outlined" sx={{ p: 2, borderRadius: 1.5, bgcolor: 'action.hover' }}>
                <Typography variant="caption" color="text.secondary" fontWeight={700}>FULL NAME</Typography>
                <Typography variant="body1" fontWeight={600} sx={{ overflowWrap: 'anywhere', mt: 0.5 }}>
                  {selectedUser.full_name || "—"}
                </Typography>
              </Paper>
            </Grid>

            <Grid item xs={12} sm={6} md={4}>
              <Paper variant="outlined" sx={{ p: 2, borderRadius: 1.5, bgcolor: 'action.hover' }}>
                <Typography variant="caption" color="text.secondary" fontWeight={700}>EMAIL ADDRESS</Typography>
                <Typography variant="body1" fontWeight={600} sx={{ mt: 0.5 }}>
                  {selectedUser.email || "—"}
                </Typography>
              </Paper>
            </Grid>

            <Grid item xs={12} sm={6} md={4}>
              <Paper variant="outlined" sx={{ p: 2, borderRadius: 1.5, bgcolor: 'action.hover' }}>
                <Typography variant="caption" color="text.secondary" fontWeight={700}>ASSIGNED ROLE</Typography>
                <Box sx={{ mt: 0.5 }}>
                  {selectedUser.role || selectedUser.roles?.[0] ? (
                    <Typography variant="caption" sx={{ display: 'inline-block', bgcolor: 'primary.50', color: 'primary.main', px: 1.5, py: 0.5, borderRadius: 1, fontWeight: 700 }}>
                      {(selectedUser.role || selectedUser.roles[0]).name}
                    </Typography>
                  ) : (
                    <Typography variant="body1" fontWeight={600} color="text.secondary">—</Typography>
                  )}
                </Box>
              </Paper>
            </Grid>
          </Grid>
        </Paper>

        {userDialog}
      </Box>
    );
  }

  return (
    <Box sx={{ p: 0 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3, alignItems: 'center' }}>
        <Box>
          <Typography variant="h5" fontWeight={800} color="primary">User Management</Typography>
          <Typography variant="body2" color="text.secondary">Create and manage system users and their access roles.</Typography>
        </Box>
        <Stack direction="row" spacing={1}>
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
                <TableCell>Role</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {userItems.map((user) => (
                <TableRow
                  key={user.id}
                  hover
                  onClick={() => setSelectedId(user.id)}
                  sx={{ cursor: 'pointer' }}
                >
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
                    {user.role || user.roles?.[0] ? (
                      <Typography variant="caption" sx={{ bgcolor: 'primary.50', color: 'primary.main', px: 1, py: 0.2, borderRadius: 1, fontWeight: 700 }}>
                        {(user.role || user.roles[0]).name}
                      </Typography>
                    ) : (
                      <Typography variant="caption" color="text.secondary">No role</Typography>
                    )}
                  </TableCell>
                  <TableCell align="right">
                    <Stack direction="row" spacing={0.5} justifyContent="flex-end">
                      {canManage && (
                        <>
                          <Tooltip title="View details">
                            <IconButton size="small" color="primary" onClick={(e) => { e.stopPropagation(); setSelectedId(user.id); }}>
                              <VisibilityOutlined fontSize="small" />
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

      {userDialog}
    </Box>
  );
}

function UserDialog({ open, onClose, user, roles, onSuccess }) {
  const [form, setForm] = useState({ username: "", full_name: "", email: "", password: "", role_id: "" });
  const [saving, setSaving] = useState(false);

  React.useEffect(() => {
    if (user) {
      const currentRole = user.role || user.roles?.[0];
      setForm({
        username: user.username,
        full_name: user.full_name || "",
        email: user.email,
        password: "",
        role_id: currentRole?.id || ""
      });
    } else {
      setForm({ username: "", full_name: "", email: "", password: "", role_id: "" });
    }
  }, [user, open]);

  const handleSave = async () => {
    if (!form.role_id) {
      toast.warning("Please select a role");
      return;
    }
    const password = form.password.trim();
    if (!user && !password) {
      toast.warning("Please enter a password");
      return;
    }
    if (password && password.length < 6) {
      toast.warning("Password must be at least 6 characters");
      return;
    }
    setSaving(true);
    try {
      if (user) {
        const payload = {
          username: form.username,
          full_name: form.full_name,
          email: form.email,
          role_id: form.role_id
        };
        if (password) {
          payload.password = password;
        }
        await usersApi.update(user.id, payload);
        toast.success("User updated");
      } else {
        await usersApi.create({ ...form, password });
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
          <TextField label="Username" fullWidth size="small" value={form.username} onChange={e => setForm({ ...form, username: e.target.value })} disabled={!!user} />
          <TextField label="Full Name" fullWidth size="small" value={form.full_name} onChange={e => setForm({ ...form, full_name: e.target.value })} />
          <TextField label="Email" fullWidth size="small" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} />
          <TextField
            label={user ? "New Password (leave blank to keep current)" : "Password"}
            type="password"
            fullWidth
            size="small"
            value={form.password}
            onChange={e => setForm({ ...form, password: e.target.value })}
          />

          <FormControl fullWidth size="small">
            <InputLabel id="user-role-label">Role</InputLabel>
            <Select
              labelId="user-role-label"
              label="Role"
              value={form.role_id}
              onChange={e => setForm({ ...form, role_id: e.target.value })}
            >
              <MenuItem value="" disabled>Select role</MenuItem>
              {roles.map(r => (
                <MenuItem key={r.id} value={r.id}>{r.name}</MenuItem>
              ))}
            </Select>
          </FormControl>
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

export default UserManagement;
