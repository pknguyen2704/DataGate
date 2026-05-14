import React, { useState } from 'react';
import {
  Box, Button, Table, TableBody, TableCell, TableHead, TableRow,
  Paper, Typography, CircularProgress, Stack, IconButton,
  Dialog, DialogTitle, DialogContent, DialogActions, TextField,
  Switch, FormControlLabel, Grid, Tooltip, TablePagination, TableContainer,
  MenuItem, Select, FormControl, InputLabel, Chip
} from "@mui/material";
import {
  RefreshOutlined, AddOutlined, EditOutlined,
  ArrowBackOutlined, VisibilityOutlined, SaveOutlined,
  StorageOutlined, SearchOutlined, CheckCircleOutline, CancelOutlined,
  BugReportOutlined, PowerSettingsNewOutlined, DeleteOutline
} from "@mui/icons-material";
import { useSelector } from "react-redux";
import { connectionsApi } from "~/apis/connectionsApi";
import { dataAssetsApi } from "~/apis/dataAssetsApi";
import { StateBox, StatusChip, TabContainer, TabButton } from "~/components/DataGate/Page";
import { useApiResource } from "~/hooks/useApiResource";
import { toast } from "react-toastify";

const INITIAL_CONNECTION = {
  connection_name: "",
  description: "",
  trino_host: "",
  trino_port: 8080,
  trino_user: "admin",
  trino_password: "",
  iceberg_rest_url: "",
  iceberg_catalog_name: "iceberg",
  iceberg_warehouse: "",
  minio_endpoint_url: "",
  minio_access_key: "",
  minio_secret_key: "",
  is_active: true
};

function PlatformConnection() {
  const { user } = useSelector(state => state.auth);
  const isAdmin = user?.roles?.some(r => r === "Admin" || r?.name === "Admin");
  const canView = isAdmin || user?.permissions?.some(p => p === "connection:view" || p?.code === "connection:view");
  const canCreate = isAdmin || user?.permissions?.some(p => p === "connection:create" || p?.code === "connection:create");
  const canUpdate = isAdmin || user?.permissions?.some(p => p === "connection:update" || p?.code === "connection:update");
  const canDelete = isAdmin;
  const canTest = isAdmin || user?.permissions?.some(p => p === "connection:test" || p?.code === "connection:test");
  const canCreateTable = isAdmin || user?.permissions?.some(p => p === "table:create" || p?.code === "table:create");
  const canUpdateTable = isAdmin || user?.permissions?.some(p => p === "table:update" || p?.code === "table:update");
  const canDeleteTable = isAdmin || user?.permissions?.some(p => p === "table:delete" || p?.code === "table:delete");

  const [selectedConnectionId, setSelectedConnectionId] = useState(null);

  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);

  const connections = useApiResource(() => connectionsApi.list({
    page: page + 1,
    page_size: pageSize
  }), [page, pageSize]);

  const [openDialog, setOpenDialog] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [form, setForm] = useState(INITIAL_CONNECTION);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);

  const handleOpenAdd = () => {
    setForm(INITIAL_CONNECTION);
    setEditingId(null);
    setOpenDialog(true);
  };

  const handleOpenEdit = (row) => {
    setForm({
      ...row,
      trino_password: "", // Don't show old password
      minio_secret_key: "", // Don't show old secret
    });
    setEditingId(row.id);
    setOpenDialog(true);
  };

  const handleToggleActive = async (row) => {
    try {
      if (row.is_active) {
        await connectionsApi.deactivate(row.id);
        toast.success("Deactivated");
      } else {
        await connectionsApi.activate(row.id);
        toast.success("Activated");
      }
      connections.reload();
    } catch (err) {
      toast.error("Action failed");
    }
  };

  const handleDeactivate = async (id) => {
    if (!window.confirm("Are you sure you want to deactivate this connection?")) return;
    try {
      await connectionsApi.deactivate(id);
      toast.success("Deactivated");
      connections.reload();
    } catch (err) {
      toast.error("Failed to deactivate");
    }
  };

  const handleTest = async () => {
    if (editingId) {
      setTesting(true);
      try {
        const res = await connectionsApi.test(editingId);
        if (res.data.success) toast.success(res.data.message);
        else toast.error(res.data.message);
      } catch (err) {
        toast.error("Test failed: " + (err.response?.data?.detail || err.message));
      } finally {
        setTesting(false);
      }
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      if (editingId) {
        await connectionsApi.update(editingId, form);
        toast.success("Updated");
      } else {
        await connectionsApi.create(form);
        toast.success("Created");
      }
      setOpenDialog(false);
      connections.reload();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Save failed");
    } finally {
      setSaving(false);
    }
  };

  if (selectedConnectionId) {
    return (
      <ConnectionDetail
        connectionId={selectedConnectionId}
        onBack={() => setSelectedConnectionId(null)}
        canUpdate={canUpdate}
        canUpdateTable={canUpdateTable}
        canCreateTable={canCreateTable}
        canDeleteTable={canDeleteTable}
        onToggleActive={handleToggleActive}
      />
    );
  }

  let rows = [];
  if (connections.data && connections.data.items) {
    rows = connections.data.items;
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2, gap: 1 }}>
        <Button startIcon={<RefreshOutlined />} variant="outlined" size="small" onClick={connections.reload} sx={{ borderRadius: 1.5 }}>
          Refresh
        </Button>
        {canCreate && (
          <Button startIcon={<AddOutlined />} variant="contained" size="small" onClick={handleOpenAdd} sx={{ borderRadius: 1.5 }}>
            Add Connection
          </Button>
        )}
      </Box>

      <StateBox loading={connections.loading} error={connections.error} empty={!rows.length}>
        <TableContainer component={Paper} variant="outlined" sx={{ borderRadius: 2, overflow: 'hidden' }}>
          <Table size="small">
            <TableHead>
              <TableRow sx={{ bgcolor: 'primary.main' }}>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Connection Name</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Description</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Status</TableCell>
                <TableCell align="right" sx={{ color: 'white', fontWeight: 'bold' }}>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.map((row) => (
                <TableRow key={row.id} hover>
                  <TableCell onClick={() => setSelectedConnectionId(row.id)} sx={{ cursor: 'pointer', fontWeight: 600 }}>{row.connection_name}</TableCell>
                  <TableCell>{row.description || "—"}</TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Switch
                        size="small"
                        checked={row.is_active}
                        onChange={() => handleToggleActive(row)}
                        color="success"
                        disabled={!canUpdate}
                      />
                      <Chip
                        label={row.is_active ? "Active" : "Inactive"}
                        size="small"
                        variant="outlined"
                        color={row.is_active ? "success" : "default"}
                        sx={{ ml: 1, border: 'none', fontWeight: 600 }}
                      />
                    </Box>
                  </TableCell>
                  <TableCell align="right">
                    <Stack direction="row" spacing={0.5} justifyContent="flex-end">
                      <Tooltip title="View Details">
                        <IconButton size="small" color="primary" onClick={() => setSelectedConnectionId(row.id)}>
                          <VisibilityOutlined fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      {canUpdate && (
                        <>
                          <Tooltip title="Edit">
                            <IconButton size="small" color="info" onClick={() => handleOpenEdit(row)}>
                              <EditOutlined fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          {row.is_active && (
                            <Tooltip title="Deactivate">
                              <IconButton size="small" color="error" onClick={() => handleDeactivate(row.id)}>
                                <PowerSettingsNewOutlined fontSize="small" />
                              </IconButton>
                            </Tooltip>
                          )}
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
            count={connections.data?.total || 0}
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

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle sx={{ fontWeight: 'bold' }}>
          {editingId ? "Edit" : "New"} Connection
        </DialogTitle>
        <DialogContent dividers>
          <Grid container spacing={2} sx={{ mt: 0.5 }}>
            <Grid item xs={12} md={6}>
              <TextField label="Name" fullWidth size="small" value={form.connection_name} onChange={e => setForm({ ...form, connection_name: e.target.value })} />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField label="Description" fullWidth size="small" value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} />
            </Grid>

            <Grid item xs={12}><Typography variant="caption" color="primary" fontWeight={800}>TRINO</Typography></Grid>
            <Grid item xs={12} md={4}>
              <TextField label="Host" fullWidth size="small" value={form.trino_host} onChange={e => setForm({ ...form, trino_host: e.target.value })} />
            </Grid>
            <Grid item xs={12} md={2}>
              <TextField label="Port" type="number" fullWidth size="small" value={form.trino_port} onChange={e => setForm({ ...form, trino_port: parseInt(e.target.value) })} />
            </Grid>
            <Grid item xs={12} md={3}>
              <TextField label="User" fullWidth size="small" value={form.trino_user} onChange={e => setForm({ ...form, trino_user: e.target.value })} />
            </Grid>
            <Grid item xs={12} md={3}>
              <TextField label="Password" type="password" fullWidth size="small" placeholder={editingId ? "••••••••" : ""} value={form.trino_password} onChange={e => setForm({ ...form, trino_password: e.target.value })} />
            </Grid>

            <Grid item xs={12}><Typography variant="caption" color="primary" fontWeight={800}>ICEBERG</Typography></Grid>
            <Grid item xs={12} md={4}>
              <TextField label="Catalog" fullWidth size="small" value={form.iceberg_catalog_name} onChange={e => setForm({ ...form, iceberg_catalog_name: e.target.value })} />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField label="REST URL" fullWidth size="small" value={form.iceberg_rest_url} onChange={e => setForm({ ...form, iceberg_rest_url: e.target.value })} />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField label="Warehouse" fullWidth size="small" value={form.iceberg_warehouse} onChange={e => setForm({ ...form, iceberg_warehouse: e.target.value })} />
            </Grid>

            <Grid item xs={12}><Typography variant="caption" color="primary" fontWeight={800}>STORAGE (MINIO/S3)</Typography></Grid>
            <Grid item xs={12} md={4}>
              <TextField label="Endpoint" fullWidth size="small" value={form.minio_endpoint_url} onChange={e => setForm({ ...form, minio_endpoint_url: e.target.value })} />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField label="Access Key" fullWidth size="small" value={form.minio_access_key} onChange={e => setForm({ ...form, minio_access_key: e.target.value })} />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField label="Secret Key" type="password" fullWidth size="small" placeholder={editingId ? "••••••••" : ""} value={form.minio_secret_key} onChange={e => setForm({ ...form, minio_secret_key: e.target.value })} />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions sx={{ p: 2, justifyContent: 'space-between' }}>
          <Box>
            {editingId && (
              <Button startIcon={<BugReportOutlined />} color="info" onClick={handleTest} disabled={testing}>
                {testing ? "Testing..." : "Test Connection"}
              </Button>
            )}
          </Box>
          <Stack direction="row" spacing={1}>
            <Button onClick={() => setOpenDialog(false)} color="inherit">Cancel</Button>
            <Button variant="contained" startIcon={<SaveOutlined />} onClick={handleSave} disabled={saving}>
              {saving ? "Saving..." : "Save"}
            </Button>
          </Stack>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

function ConnectionDetail({ connectionId, onBack, canUpdate, canUpdateTable, canCreateTable, canDeleteTable, onToggleActive }) {
  const [tab, setTab] = useState("config");
  const connection = useApiResource(() => connectionsApi.get(connectionId));

  if (connection.loading) return <Box sx={{ p: 10, textAlign: 'center' }}><CircularProgress /></Box>;

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <IconButton onClick={onBack} sx={{ mr: 1 }} color="primary"><ArrowBackOutlined /></IconButton>
        <Typography variant="h6" fontWeight={700}>{connection.data?.connection_name}</Typography>
      </Box>

      <TabContainer>
        <TabButton active={tab === "config"} onClick={() => setTab("config")} label="Configuration" />
        <TabButton active={tab === "tables"} onClick={() => setTab("tables")} label="Managed Tables" />
      </TabContainer>

      {tab === "config" && (
        <Paper variant="outlined" sx={{ p: 3, borderRadius: 2 }}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="h6" color="primary" fontWeight={700} sx={{ mb: 2, borderBottom: '1px solid', borderColor: 'divider', pb: 1 }}>General Info</Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="caption" color="text.secondary" fontWeight={700}>DESCRIPTION</Typography>
              <Typography variant="body2">{connection.data.description || "N/A"}</Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="caption" color="text.secondary" fontWeight={700}>STATUS</Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', mt: 0.5 }}>
                <Switch
                  size="small"
                  checked={connection.data.is_active}
                  onChange={() => onToggleActive(connection.data)}
                  color="success"
                  disabled={!canUpdate}
                />
                <Chip
                  label={connection.data.is_active ? "Active" : "Inactive"}
                  size="small"
                  variant="outlined"
                  color={connection.data.is_active ? "success" : "default"}
                  sx={{ ml: 1, border: 'none', fontWeight: 600 }}
                />
              </Box>
            </Grid>

            <Grid item xs={12}>
              <Typography variant="h6" color="primary" fontWeight={700} sx={{ mt: 2, mb: 2, borderBottom: '1px solid', borderColor: 'divider', pb: 1 }}>Trino Configuration</Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="caption" color="text.secondary" fontWeight={700}>HOST</Typography>
              <Typography variant="body2">{connection.data.trino_host}</Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="caption" color="text.secondary" fontWeight={700}>PORT</Typography>
              <Typography variant="body2">{connection.data.trino_port}</Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="caption" color="text.secondary" fontWeight={700}>USER</Typography>
              <Typography variant="body2">{connection.data.trino_user}</Typography>
            </Grid>

            <Grid item xs={12}>
              <Typography variant="h6" color="primary" fontWeight={700} sx={{ mt: 2, mb: 2, borderBottom: '1px solid', borderColor: 'divider', pb: 1 }}>Iceberg Configuration</Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="caption" color="text.secondary" fontWeight={700}>CATALOG NAME</Typography>
              <Typography variant="body2">{connection.data.iceberg_catalog_name}</Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="caption" color="text.secondary" fontWeight={700}>REST URL</Typography>
              <Typography variant="body2">{connection.data.iceberg_rest_url}</Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="caption" color="text.secondary" fontWeight={700}>WAREHOUSE</Typography>
              <Typography variant="body2" sx={{ wordBreak: 'break-all' }}>{connection.data.iceberg_warehouse}</Typography>
            </Grid>

            <Grid item xs={12}>
              <Typography variant="h6" color="primary" fontWeight={700} sx={{ mt: 2, mb: 2, borderBottom: '1px solid', borderColor: 'divider', pb: 1 }}>Storage (MinIO/S3) Configuration</Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="caption" color="text.secondary" fontWeight={700}>ENDPOINT URL</Typography>
              <Typography variant="body2">{connection.data.minio_endpoint_url}</Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="caption" color="text.secondary" fontWeight={700}>ACCESS KEY</Typography>
              <Typography variant="body2">{connection.data.minio_access_key}</Typography>
            </Grid>
          </Grid>
        </Paper>
      )}

      {tab === "tables" && (
        <ManagedTables connectionId={connectionId} connectionData={connection.data} canUpdateTable={canUpdateTable} canCreateTable={canCreateTable} canDeleteTable={canDeleteTable} />
      )}
    </Box>
  );
}

function ManagedTables({ connectionId, connectionData, canUpdateTable, canCreateTable, canDeleteTable }) {
  const [tables, setTables] = useState({ data: [], loading: true });
  const [openAdd, setOpenAdd] = useState(false);
  const [adding, setAdding] = useState(false);

  const [schemas, setSchemas] = useState([]);
  const [loadingSchemas, setLoadingSchemas] = useState(false);
  const [selectedSchema, setSelectedSchema] = useState("");

  const [discoveryTables, setDiscoveryTables] = useState([]);
  const [loadingDiscovery, setLoadingDiscovery] = useState(false);
  const [selectedTable, setSelectedTable] = useState("");

  const refreshManaged = async () => {
    setTables(prev => ({ ...prev, loading: true }));
    try {
      const res = await connectionsApi.list();
    } catch (err) { }
  };

  const managedRes = useApiResource(() => dataAssetsApi.list({ connection_id: connectionId }), [connectionId]);

  const fetchSchemas = async () => {
    setLoadingSchemas(true);
    try {
      const res = await connectionsApi.discover(connectionId);
      setSchemas(res.data || []);
    } catch (err) {
      toast.error("Discovery failed");
    } finally {
      setLoadingSchemas(false);
    }
  };

  const fetchDiscoveryTables = async (schemaName) => {
    setLoadingDiscovery(true);
    try {
      const res = await connectionsApi.discover(connectionId, schemaName);
      setDiscoveryTables(res.data || []);
    } catch (err) {
      toast.error("Table discovery failed");
    } finally {
      setLoadingDiscovery(false);
    }
  };

  const handleRegister = async () => {
    setAdding(true);
    try {
      await connectionsApi.addManagedTable(connectionId, {
        catalog: connectionData.iceberg_catalog_name,
        schema: selectedSchema,
        table_name: selectedTable
      });
      toast.success("Table registered");
      setOpenAdd(false);
      managedRes.reload();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Registration failed");
    } finally {
      setAdding(false);
    }
  };

  const handleToggleTableActive = async (table) => {
    try {
      if (table.is_active) {
        await dataAssetsApi.deactivate(table.id);
        toast.success("Table deactivated");
      } else {
        await dataAssetsApi.activate(table.id);
        toast.success("Table activated");
      }
      managedRes.reload();
    } catch (err) {
      toast.error("Action failed");
    }
  };

  const handleDelete = async (tableId) => {
    if (!window.confirm("Remove this table from management?")) return;
    try {
      await connectionsApi.removeManagedTable(connectionId, tableId);
      toast.success("Removed");
      managedRes.reload();
    } catch (err) {
      toast.error("Removal failed");
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
        {canCreateTable && (
          <Button startIcon={<AddOutlined />} variant="contained" size="small" onClick={() => { setOpenAdd(true); fetchSchemas(); }}>
            Register Table
          </Button>
        )}
      </Box>

      <StateBox loading={managedRes.loading} error={managedRes.error} empty={!(managedRes.data?.items || []).length}>
        <Paper variant="outlined" sx={{ borderRadius: 2 }}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Schema</TableCell>
                <TableCell>Table Name</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {(managedRes.data?.items || []).map((row) => (
                <TableRow key={row.id}>
                  <TableCell>{row.schema_name}</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>{row.table_name}</TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Switch
                        size="small"
                        checked={row.is_active}
                        onChange={() => handleToggleTableActive(row)}
                        color="success"
                        disabled={!canUpdateTable}
                      />
                      <Chip
                        label={row.is_active ? "Active" : "Inactive"}
                        size="small"
                        variant="outlined"
                        color={row.is_active ? "success" : "default"}
                        sx={{ ml: 1, border: 'none', fontWeight: 600 }}
                      />
                    </Box>
                  </TableCell>
                  <TableCell align="right">
                    {canDeleteTable && (
                      <IconButton size="small" color="error" onClick={() => handleDelete(row.id)}>
                        <DeleteOutline fontSize="small" />
                      </IconButton>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Paper>
      </StateBox>

      <Dialog open={openAdd} onClose={() => setOpenAdd(false)} maxWidth="xs" fullWidth>
        <DialogTitle sx={{ fontWeight: 700 }}>Register Managed Table</DialogTitle>
        <DialogContent dividers>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <FormControl fullWidth size="small">
              <InputLabel>Schema</InputLabel>
              <Select value={selectedSchema} label="Schema" onChange={e => { setSelectedSchema(e.target.value); fetchDiscoveryTables(e.target.value); }}>
                {loadingSchemas ? <MenuItem disabled>Loading...</MenuItem> : schemas.map(s => <MenuItem key={s} value={s}>{s}</MenuItem>)}
              </Select>
            </FormControl>
            <FormControl fullWidth size="small" disabled={!selectedSchema}>
              <InputLabel>Table</InputLabel>
              <Select value={selectedTable} label="Table" onChange={e => setSelectedTable(e.target.value)}>
                {loadingDiscovery ? <MenuItem disabled>Discovering...</MenuItem> : discoveryTables.map(t => <MenuItem key={t} value={t}>{t}</MenuItem>)}
              </Select>
            </FormControl>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenAdd(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleRegister} disabled={!selectedTable || adding}>
            {adding ? "Registering..." : "Register"}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default PlatformConnection;