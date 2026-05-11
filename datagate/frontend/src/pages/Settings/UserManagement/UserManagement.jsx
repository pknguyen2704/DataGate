import React, { useState } from 'react';
import { 
  Box, Button, Table, TableBody, TableCell, TableHead, TableRow, 
  Paper, Stack, IconButton, Dialog, DialogTitle, DialogContent, 
  DialogActions, TextField, Checkbox, FormControlLabel, FormGroup,
  Typography, Grid
} from "@mui/material";
import { 
  RefreshOutlined, EditOutlined, DeleteOutline, AddOutlined, SaveOutlined 
} from "@mui/icons-material";
import { rolesApi } from "~/apis/rolesApi";
import { usersApi } from "~/apis/usersApi";
import { StateBox, StatusChip, TabContainer, TabButton } from "~/components/DataGate/Page";
import { useApiResource } from "~/hooks/useApiResource";
import { toast } from "react-toastify";

function UserManagement() {
  const [tab, setTab] = useState("users");
  const users = useApiResource(() => usersApi.list());
  const roles = useApiResource(() => rolesApi.list());
  const permissions = useApiResource(() => rolesApi.listPermissions());

  const [openUser, setOpenUser] = useState(false);
  const [openRole, setOpenRole] = useState(false);
  const [editingItem, setEditingItem] = useState(null);

  const refresh = () => {
    users.reload();
    roles.reload();
  };

  const handleOpenAdd = () => {
    setEditingItem(null);
    if (tab === "users") setOpenUser(true);
    else setOpenRole(true);
  };

  return (
    <Box sx={{ p: { xs: 2, md: 3 } }}>
      <Stack spacing={3}>
        <Paper variant="outlined" sx={{ p: 2.5, borderRadius: 2, bgcolor: 'white', display: 'flex', justifyContent: 'space-between', alignItems: 'center', border: '1px solid', borderColor: 'divider', boxShadow: '0 2px 10px rgba(0,0,0,0.02)' }}>
          <Box>
            <Typography variant="h5" sx={{ fontWeight: 800, color: 'primary.main' }}>User & RBAC Management</Typography>
            <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>Control system access, define roles, and assign granular permissions.</Typography>
          </Box>
          <Stack direction="row" spacing={2}>
            <TabContainer sx={{ mb: 0, p: 0.5, bgcolor: 'grey.100' }}>
              <TabButton active={tab === "users"} onClick={() => setTab("users")} label="Users" />
              <TabButton active={tab === "roles"} onClick={() => setTab("roles")} label="Roles" />
            </TabContainer>
            <Button startIcon={<AddOutlined />} variant="contained" onClick={handleOpenAdd} sx={{ borderRadius: 1.5 }}>
              Add {tab === "users" ? "User" : "Role"}
            </Button>
            <Button startIcon={<RefreshOutlined />} variant="outlined" onClick={refresh} sx={{ borderRadius: 1.5 }}>
              Refresh
            </Button>
          </Stack>
        </Paper>

        {tab === "users" ? (
          <UserTable 
            resource={users} 
            onEdit={(u) => { setEditingItem(u); setOpenUser(true); }} 
          />
        ) : (
          <RoleTable 
            resource={roles} 
            onEdit={(r) => { setEditingItem(r); setOpenRole(true); }} 
          />
        )}
      </Stack>

      <UserDialog 
        open={openUser} 
        onClose={() => setOpenUser(false)} 
        item={editingItem} 
        roles={roles.data || []}
        onSuccess={refresh}
      />
      <RoleDialog 
        open={openRole} 
        onClose={() => setOpenRole(false)} 
        item={editingItem} 
        permissions={permissions.data || []}
        onSuccess={refresh}
      />
    </Box>
  );
}

function UserDialog({ open, onClose, item, roles, onSuccess }) {
  const [form, setForm] = useState({ username: "", email: "", password: "", role_ids: [] });
  const [saving, setSaving] = useState(false);

  React.useEffect(() => {
    if (item) setForm({ username: item.username, email: item.email, password: "", role_ids: (item.roles || []).map(r => r.id) });
    else setForm({ username: "", email: "", password: "", role_ids: [] });
  }, [item, open]);

  const handleSave = async () => {
    setSaving(true);
    try {
      const payload = { ...form };
      if (item && !payload.password) delete payload.password;
      
      if (item) {
        await usersApi.update(item.id, payload);
        toast.success("User updated");
      } else {
        await usersApi.create(payload);
        toast.success("User created");
      }
      onSuccess();
      onClose();
    } catch (err) {
      toast.error("Failed to save user");
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth PaperProps={{ sx: { borderRadius: 2 } }}>
      <DialogTitle sx={{ bgcolor: '#1E40AF', color: 'white', fontWeight: 'bold', py: 2 }}>
        {item ? "Edit User" : "Create New User"}
      </DialogTitle>
      <DialogContent dividers sx={{ p: 3 }}>
        <Stack spacing={3}>
          <TextField label="Username" fullWidth size="small" value={form.username} onChange={e => setForm({...form, username: e.target.value})} />
          <TextField label="Email" fullWidth size="small" value={form.email} onChange={e => setForm({...form, email: e.target.value})} />
          {!item && <TextField label="Password" type="password" fullWidth size="small" value={form.password} onChange={e => setForm({...form, password: e.target.value})} />}
          
          <Box>
            <Typography variant="subtitle2" sx={{ mb: 1.5, fontWeight: 'bold' }}>Assign Roles</Typography>
            <Paper variant="outlined" sx={{ p: 2, borderRadius: 2, bgcolor: '#F8FAFC' }}>
              <FormGroup row>
                {roles.map(r => (
                  <FormControlLabel 
                    key={r.id}
                    control={
                      <Checkbox 
                        checked={form.role_ids.includes(r.id)} 
                        onChange={e => {
                          const newIds = e.target.checked ? [...form.role_ids, r.id] : form.role_ids.filter(id => id !== r.id);
                          setForm({...form, role_ids: newIds});
                        }}
                      />
                    }
                    label={r.name}
                  />
                ))}
              </FormGroup>
            </Paper>
          </Box>
        </Stack>
      </DialogContent>
      <DialogActions sx={{ p: 2.5, gap: 1 }}>
        <Button onClick={onClose} color="inherit" sx={{ fontWeight: 'bold' }}>Cancel</Button>
        <Button variant="contained" onClick={handleSave} disabled={saving} sx={{ fontWeight: 'bold', px: 4 }}>
          {saving ? "Saving..." : "Save User"}
        </Button>
      </DialogActions>
    </Dialog>
  );
}

function RoleDialog({ open, onClose, item, permissions, onSuccess }) {
  const [form, setForm] = useState({ name: "", description: "", permission_ids: [] });
  const [saving, setSaving] = useState(false);

  React.useEffect(() => {
    if (item) setForm({ 
      name: item.name, 
      description: item.description || "", 
      permission_ids: (item.permissions || []).map(p => p.id) 
    });
    else setForm({ name: "", description: "", permission_ids: [] });
  }, [item, open]);

  const handleSave = async () => {
    setSaving(true);
    try {
      const payload = {
        name: form.name,
        description: form.description,
        permission_ids: form.permission_ids
      };

      if (item) {
        await rolesApi.update(item.id, payload);
        toast.success("Role & Permissions updated");
      } else {
        await rolesApi.create(payload);
        toast.success("Role created with permissions");
      }
      onSuccess();
      onClose();
    } catch (err) {
      toast.error("Failed to save role");
    } finally {
      setSaving(false);
    }
  };

  const groupedPerms = React.useMemo(() => {
    const groups = {};
    permissions.forEach(p => {
      const group = p.group || "General";
      if (!groups[group]) groups[group] = [];
      groups[group].push(p);
    });
    return groups;
  }, [permissions]);

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth PaperProps={{ sx: { borderRadius: 2 } }}>
      <DialogTitle sx={{ bgcolor: '#1E40AF', color: 'white', fontWeight: 'bold', py: 2 }}>
        {item ? "Edit Role & Permissions" : "Create New Role"}
      </DialogTitle>
      <DialogContent dividers sx={{ p: 3 }}>
        <Stack spacing={3}>
          <Stack direction="row" spacing={2}>
            <TextField label="Role Name" fullWidth size="small" value={form.name} onChange={e => setForm({...form, name: e.target.value})} />
            <TextField label="Description" fullWidth size="small" value={form.description} onChange={e => setForm({...form, description: e.target.value})} />
          </Stack>
          
          <Box>
            <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 'bold', color: 'primary.main' }}>Permissions Configuration</Typography>
            <Grid container spacing={2}>
              {Object.entries(groupedPerms).map(([group, perms]) => (
                <Grid item xs={12} md={6} key={group}>
                  <Paper variant="outlined" sx={{ p: 2, borderRadius: 2, height: '100%', bgcolor: '#F8FAFC' }}>
                    <Typography variant="caption" sx={{ fontWeight: 800, textTransform: 'uppercase', color: 'text.secondary', mb: 1, display: 'block' }}>
                      {group}
                    </Typography>
                    <FormGroup>
                      {perms.map(p => (
                        <FormControlLabel 
                          key={p.id}
                          control={
                            <Checkbox 
                              size="small"
                              checked={form.permission_ids.includes(p.id)} 
                              onChange={e => {
                                const newIds = e.target.checked ? [...form.permission_ids, p.id] : form.permission_ids.filter(id => id !== p.id);
                                setForm({...form, permission_ids: newIds});
                              }}
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
      <DialogActions sx={{ p: 2.5, gap: 1 }}>
        <Button onClick={onClose} color="inherit" sx={{ fontWeight: 'bold' }}>Cancel</Button>
        <Button variant="contained" onClick={handleSave} disabled={saving} sx={{ fontWeight: 'bold', px: 4 }}>
          {saving ? "Saving..." : "Save Role"}
        </Button>
      </DialogActions>
    </Dialog>
  );
}

function UserTable({ resource, onEdit }) {
  const rows = resource.data?.items || resource.data || [];
  
  const handleDelete = async (id) => {
    if (!window.confirm("Delete user?")) return;
    try {
      await usersApi.delete(id);
      toast.success("User deleted");
      resource.reload();
    } catch (err) { toast.error("Failed to delete"); }
  };

  return (
    <StateBox loading={resource.loading} error={resource.error} empty={!rows.length}>
      <Paper variant="outlined" sx={{ borderRadius: 2, overflow: 'hidden', bgcolor: 'white', border: '1px solid', borderColor: 'divider', boxShadow: '0 4px 20px rgba(0,0,0,0.03)' }}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell sx={{ bgcolor: '#1E40AF !important', color: 'white !important', fontWeight: 'bold', py: 2 }}>Username</TableCell>
              <TableCell sx={{ bgcolor: '#1E40AF !important', color: 'white !important', fontWeight: 'bold', py: 2 }}>Email</TableCell>
              <TableCell sx={{ bgcolor: '#1E40AF !important', color: 'white !important', fontWeight: 'bold', py: 2 }}>Roles</TableCell>
              <TableCell sx={{ bgcolor: '#1E40AF !important', color: 'white !important', fontWeight: 'bold', py: 2 }}>Status</TableCell>
              <TableCell align="right" sx={{ bgcolor: '#1E40AF !important', color: 'white !important', fontWeight: 'bold', py: 2 }}>Action</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {rows.map((row) => (
              <TableRow key={row.id} hover>
                <TableCell sx={{ fontWeight: 600 }}>{row.username}</TableCell>
                <TableCell>{row.email}</TableCell>
                <TableCell>
                  <Stack direction="row" spacing={0.5} flexWrap="wrap">
                    {(row.roles || []).map((role) => (
                      <Typography key={role.id} variant="caption" sx={{ bgcolor: 'primary.50', color: 'primary.main', px: 1, py: 0.2, borderRadius: 1, fontWeight: 'bold' }}>
                        {role.name}
                      </Typography>
                    ))}
                  </Stack>
                </TableCell>
                <TableCell><StatusChip value={row.is_active ? "active" : "inactive"} /></TableCell>
                <TableCell align="right">
                  <Stack direction="row" spacing={1} justifyContent="flex-end">
                    <IconButton size="small" color="primary" onClick={() => onEdit(row)} sx={{ bgcolor: 'primary.50', '&:hover': { bgcolor: 'primary.100' } }}>
                      <EditOutlined fontSize="small" />
                    </IconButton>
                    <IconButton size="small" color="error" onClick={() => handleDelete(row.id)} sx={{ bgcolor: 'error.50', '&:hover': { bgcolor: 'error.100' } }}>
                      <DeleteOutline fontSize="small" />
                    </IconButton>
                  </Stack>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Paper>
    </StateBox>
  );
}

function RoleTable({ resource, onEdit }) {
  const rows = resource.data || [];

  const handleDelete = async (id) => {
    if (!window.confirm("Delete role?")) return;
    try {
      await rolesApi.delete(id);
      toast.success("Role deleted");
      resource.reload();
    } catch (err) { toast.error("Failed to delete"); }
  };

  return (
    <StateBox loading={resource.loading} error={resource.error} empty={!rows.length}>
      <Paper variant="outlined" sx={{ borderRadius: 2, overflow: 'hidden', bgcolor: 'white', border: '1px solid', borderColor: 'divider', boxShadow: '0 4px 20px rgba(0,0,0,0.03)' }}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell sx={{ bgcolor: '#1E40AF !important', color: 'white !important', fontWeight: 'bold', py: 2 }}>Role Name</TableCell>
              <TableCell sx={{ bgcolor: '#1E40AF !important', color: 'white !important', fontWeight: 'bold', py: 2 }}>Permissions Count</TableCell>
              <TableCell sx={{ bgcolor: '#1E40AF !important', color: 'white !important', fontWeight: 'bold', py: 2 }}>Status</TableCell>
              <TableCell align="right" sx={{ bgcolor: '#1E40AF !important', color: 'white !important', fontWeight: 'bold', py: 2 }}>Action</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {rows.map((row) => (
              <TableRow key={row.id} hover>
                <TableCell sx={{ fontWeight: 600 }}>{row.name}</TableCell>
                <TableCell>
                  <Typography variant="body2" sx={{ fontWeight: 'bold', color: 'secondary.main' }}>
                    {(row.permissions || []).length} permissions
                  </Typography>
                </TableCell>
                <TableCell><StatusChip value={row.is_active ? "active" : "inactive"} /></TableCell>
                <TableCell align="right">
                  <Stack direction="row" spacing={1} justifyContent="flex-end">
                    <IconButton size="small" color="primary" onClick={() => onEdit(row)} sx={{ bgcolor: 'primary.50', '&:hover': { bgcolor: 'primary.100' } }}>
                      <EditOutlined fontSize="small" />
                    </IconButton>
                    <IconButton size="small" color="error" onClick={() => handleDelete(row.id)} sx={{ bgcolor: 'error.50', '&:hover': { bgcolor: 'error.100' } }}>
                      <DeleteOutline fontSize="small" />
                    </IconButton>
                  </Stack>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Paper>
    </StateBox>
  );
}

export default UserManagement;