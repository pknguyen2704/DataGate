import React, { useState } from 'react';
import { 
  Box, Button, Table, TableBody, TableCell, TableHead, TableRow, 
  Paper, Typography, CircularProgress, Stack, IconButton,
  Dialog, DialogTitle, DialogContent, DialogActions, TextField,
  Switch, FormControlLabel, Grid
} from "@mui/material";
import { 
  RefreshOutlined, AddOutlined, EditOutlined, DeleteOutline, 
  ArrowBackOutlined, VisibilityOutlined, SaveOutlined, 
  StorageOutlined, SearchOutlined, CheckCircleOutline, CancelOutlined
} from "@mui/icons-material";
import { MenuItem, Select, FormControl, InputLabel } from "@mui/material";
import { connectionsApi } from "~/apis/connectionsApi";
import { tablesApi } from "~/apis/tablesApi";
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
  const [selectedConnectionId, setSelectedConnectionId] = useState(null);
  const connections = useApiResource(() => connectionsApi.list());

  const [openDialog, setOpenDialog] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [form, setForm] = useState(INITIAL_CONNECTION);
  const [saving, setSaving] = useState(false);

  const handleOpenAdd = () => {
    setForm(INITIAL_CONNECTION);
    setEditingId(null);
    setOpenDialog(true);
  };

  const handleOpenEdit = (row) => {
    setForm({
      connection_name: row.connection_name || "",
      description: row.description || "",
      trino_host: row.trino_host || "",
      trino_port: row.trino_port || 8080,
      trino_user: row.trino_user || "admin",
      trino_password: row.trino_password || "",
      iceberg_rest_url: row.iceberg_rest_url || "",
      iceberg_catalog_name: row.iceberg_catalog_name || "iceberg",
      iceberg_warehouse: row.iceberg_warehouse || "",
      minio_endpoint_url: row.minio_endpoint_url || "",
      minio_access_key: row.minio_access_key || "",
      minio_secret_key: row.minio_secret_key || "",
      is_active: row.is_active ?? true
    });
    setEditingId(row.id);
    setOpenDialog(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure? This will remove all associated metadata.")) return;
    try {
      await connectionsApi.delete(id);
      toast.success("Deleted");
      connections.reload();
    } catch (err) {
      toast.error("Failed to delete");
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
      toast.error("Save failed");
    } finally {
      setSaving(false);
    }
  };

  if (selectedConnectionId) {
    return (
      <ConnectionDetail 
        connectionId={selectedConnectionId} 
        onBack={() => setSelectedConnectionId(null)} 
      />
    );
  }

  const rows = connections.data || [];

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2, gap: 1 }}>
        <Button startIcon={<RefreshOutlined />} variant="outlined" size="small" onClick={connections.reload} sx={{ borderRadius: 1.5 }}>
          Refresh
        </Button>
        <Button startIcon={<AddOutlined />} variant="contained" size="small" onClick={handleOpenAdd} sx={{ borderRadius: 1.5 }}>
          Add Connection
        </Button>
      </Box>

      <StateBox loading={connections.loading} error={connections.error} empty={!rows.length}>
        <Paper variant="outlined" sx={{ borderRadius: 2, overflow: 'hidden', border: '1px solid', borderColor: 'divider' }}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell sx={{ bgcolor: '#1E40AF !important', color: 'white !important', fontWeight: 'bold' }}>Name</TableCell>
                <TableCell sx={{ bgcolor: '#1E40AF !important', color: 'white !important', fontWeight: 'bold' }}>Trino Host</TableCell>
                <TableCell sx={{ bgcolor: '#1E40AF !important', color: 'white !important', fontWeight: 'bold' }}>Catalog</TableCell>
                <TableCell sx={{ bgcolor: '#1E40AF !important', color: 'white !important', fontWeight: 'bold' }}>Status</TableCell>
                <TableCell align="right" sx={{ bgcolor: '#1E40AF !important', color: 'white !important', fontWeight: 'bold' }}>Action</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.map((row) => (
                <TableRow key={row.id} hover>
                  <TableCell onClick={() => setSelectedConnectionId(row.id)} sx={{ cursor: 'pointer', fontWeight: 500 }}>{row.connection_name}</TableCell>
                  <TableCell>{row.trino_host}:{row.trino_port}</TableCell>
                  <TableCell>{row.iceberg_catalog_name}</TableCell>
                  <TableCell><StatusChip value={row.is_active ? "active" : "inactive"} /></TableCell>
                  <TableCell align="right">
                    <IconButton size="small" color="primary" sx={{ mr: 0.5, bgcolor: 'primary.50' }} onClick={() => setSelectedConnectionId(row.id)}>
                      <VisibilityOutlined fontSize="small" />
                    </IconButton>
                    <IconButton size="small" color="info" sx={{ mr: 0.5, bgcolor: 'info.50' }} onClick={() => handleOpenEdit(row)}>
                      <EditOutlined fontSize="small" />
                    </IconButton>
                    <IconButton size="small" color="error" sx={{ bgcolor: 'error.50' }} onClick={() => handleDelete(row.id)}>
                      <DeleteOutline fontSize="small" />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Paper>
      </StateBox>

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth PaperProps={{ sx: { borderRadius: 2 } }}>
        <DialogTitle sx={{ bgcolor: '#1E40AF', color: 'white', fontWeight: 'bold', py: 2 }}>
          {editingId ? "Edit" : "New"} Platform Connection
        </DialogTitle>
        <DialogContent dividers sx={{ p: 3 }}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <TextField 
                label="Connection Name" 
                fullWidth size="small" 
                value={form.connection_name}
                onChange={e => setForm({...form, connection_name: e.target.value})}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField 
                label="Description" 
                fullWidth size="small" 
                value={form.description}
                onChange={e => setForm({...form, description: e.target.value})}
              />
            </Grid>
            
            <Grid item xs={12}><Typography variant="subtitle2" color="primary" fontWeight="bold">Trino Configuration</Typography></Grid>
            <Grid item xs={12} md={6}>
              <TextField 
                label="Trino Host" 
                fullWidth size="small" 
                value={form.trino_host}
                onChange={e => setForm({...form, trino_host: e.target.value})}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField 
                label="Trino Port" 
                type="number"
                fullWidth size="small" 
                value={form.trino_port}
                onChange={e => setForm({...form, trino_port: parseInt(e.target.value)})}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField 
                label="Trino User" 
                fullWidth size="small" 
                value={form.trino_user}
                onChange={e => setForm({...form, trino_user: e.target.value})}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField 
                label="Trino Password" 
                type="password"
                fullWidth size="small" 
                value={form.trino_password}
                onChange={e => setForm({...form, trino_password: e.target.value})}
              />
            </Grid>

            <Grid item xs={12}><Typography variant="subtitle2" color="primary" fontWeight="bold">Iceberg Configuration</Typography></Grid>
            <Grid item xs={12} md={4}>
              <TextField 
                label="Catalog Name" 
                fullWidth size="small" 
                value={form.iceberg_catalog_name}
                onChange={e => setForm({...form, iceberg_catalog_name: e.target.value})}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField 
                label="REST URL" 
                fullWidth size="small" 
                value={form.iceberg_rest_url}
                onChange={e => setForm({...form, iceberg_rest_url: e.target.value})}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField 
                label="Warehouse" 
                fullWidth size="small" 
                value={form.iceberg_warehouse}
                onChange={e => setForm({...form, iceberg_warehouse: e.target.value})}
              />
            </Grid>

            <Grid item xs={12}><Typography variant="subtitle2" color="primary" fontWeight="bold">MinIO/S3 Storage</Typography></Grid>
            <Grid item xs={12} md={4}>
              <TextField 
                label="Endpoint URL" 
                fullWidth size="small" 
                value={form.minio_endpoint_url}
                onChange={e => setForm({...form, minio_endpoint_url: e.target.value})}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField 
                label="Access Key" 
                fullWidth size="small" 
                value={form.minio_access_key}
                onChange={e => setForm({...form, minio_access_key: e.target.value})}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField 
                label="Secret Key" 
                type="password"
                fullWidth size="small" 
                value={form.minio_secret_key}
                onChange={e => setForm({...form, minio_secret_key: e.target.value})}
              />
            </Grid>

            <Grid item xs={12}>
              <FormControlLabel 
                control={<Switch checked={form.is_active} onChange={e => setForm({...form, is_active: e.target.checked})} />}
                label="Active Status"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions sx={{ p: 2.5, gap: 1 }}>
          <Button onClick={() => setOpenDialog(false)} color="inherit" sx={{ fontWeight: 'bold' }}>Cancel</Button>
          <Button variant="contained" startIcon={<SaveOutlined />} onClick={handleSave} disabled={saving} sx={{ fontWeight: 'bold', px: 4 }}>
            {saving ? "Saving..." : editingId ? "Update" : "Create"}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

function ConnectionDetail({ connectionId, onBack }) {
  const [tab, setTab] = useState("config");
  const connection = useApiResource(() => connectionsApi.get(connectionId));

  if (connection.loading) return <CircularProgress />;

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <IconButton onClick={onBack} sx={{ mr: 1 }} color="primary">
          <ArrowBackOutlined />
        </IconButton>
        <Typography variant="h6" fontWeight="bold">
          {connection.data?.connection_name || 'Connection Details'}
        </Typography>
      </Box>

      <TabContainer>
        <TabButton 
          active={tab === "config"}
          onClick={() => setTab("config")}
          label="Configuration"
        />
        <TabButton 
          active={tab === "tables"}
          onClick={() => setTab("tables")}
          label="Managed Tables"
        />
      </TabContainer>

      {tab === "config" && (
        <Paper sx={{ p: 4, borderRadius: 2 }} variant="outlined">
          <Typography variant="subtitle1" fontWeight="bold" gutterBottom color="primary">Connection Parameters</Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={4}>
              <Typography variant="caption" color="text.secondary">Trino Host</Typography>
              <Typography variant="body2" fontWeight={500}>{connection.data.trino_host}:{connection.data.trino_port}</Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="caption" color="text.secondary">Iceberg Catalog</Typography>
              <Typography variant="body2" fontWeight={500}>{connection.data.iceberg_catalog_name}</Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="caption" color="text.secondary">MinIO Endpoint</Typography>
              <Typography variant="body2" fontWeight={500}>{connection.data.minio_endpoint_url}</Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="caption" color="text.secondary">Iceberg Warehouse</Typography>
              <Typography variant="body2" fontWeight={500}>{connection.data.iceberg_warehouse}</Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="caption" color="text.secondary">Created At</Typography>
              <Typography variant="body2" fontWeight={500}>{new Date(connection.data.created_at).toLocaleString()}</Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="caption" color="text.secondary">Status</Typography>
              <Box><StatusChip value={connection.data.is_active ? "active" : "inactive"} /></Box>
            </Grid>
          </Grid>
        </Paper>
      )}

      {tab === "tables" && (
        <ManagedTables connectionId={connectionId} connectionData={connection.data} />
      )}
    </Box>
  );
}

function ManagedTables({ connectionId, connectionData }) {
  const tables = useApiResource(() => tablesApi.list({ connection_id: connectionId }), [connectionId]);
  const [openAdd, setOpenAdd] = useState(false);
  const [adding, setAdding] = useState(false);
  
  const [schemas, setSchemas] = useState([]);
  const [loadingSchemas, setLoadingSchemas] = useState(false);
  const [selectedSchema, setSelectedSchema] = useState("");
  
  const [discoveryTables, setDiscoveryTables] = useState([]);
  const [loadingDiscovery, setLoadingDiscovery] = useState(false);
  const [selectedTable, setSelectedTable] = useState("");

  const fetchSchemas = async () => {
    setLoadingSchemas(true);
    try {
      const res = await connectionsApi.listSchemas(connectionId);
      setSchemas(res.data || []);
    } catch (err) {
      toast.error("Failed to fetch schemas");
    } finally {
      setLoadingSchemas(false);
    }
  };

  const fetchDiscoveryTables = async (schemaName) => {
    setLoadingDiscovery(true);
    try {
      const res = await connectionsApi.listTables(connectionId, schemaName);
      setDiscoveryTables(res.data || []);
    } catch (err) {
      toast.error("Failed to fetch tables from schema: " + schemaName);
    } finally {
      setLoadingDiscovery(false);
    }
  };

  const handleOpenAdd = () => {
    setSelectedSchema("");
    setSelectedTable("");
    setDiscoveryTables([]);
    setOpenAdd(true);
    fetchSchemas();
  };

  const handleSchemaChange = (e) => {
    const val = e.target.value;
    setSelectedSchema(val);
    setSelectedTable("");
    if (val) {
      fetchDiscoveryTables(val);
    }
  };

  const handleRegister = async () => {
    if (!selectedSchema || !selectedTable) return;
    setAdding(true);
    try {
      await tablesApi.create({
        connection_id: connectionId,
        catalog_name: connectionData.iceberg_catalog_name,
        schema_name: selectedSchema,
        table_name: selectedTable,
        is_active: true
      });
      toast.success(`Registered table: ${selectedTable}`);
      setOpenAdd(false);
      tables.reload();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to register table");
    } finally {
      setAdding(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Unregister this table? This will not delete data in Iceberg but will remove it from DataGate.")) return;
    try {
      await tablesApi.delete(id);
      toast.success("Unregistered successfully");
      tables.reload();
    } catch (err) {
      toast.error("Failed to unregister");
    }
  };

  const handleToggleActive = async (row) => {
    try {
      if (row.is_active) {
        await tablesApi.deactivate(row.id);
      } else {
        await tablesApi.activate(row.id);
      }
      tables.reload();
    } catch (err) {
      toast.error("Failed to update status");
    }
  };

  const rows = tables.data || [];

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
        <Button 
          startIcon={<AddOutlined />} 
          variant="contained" 
          size="small" 
          onClick={handleOpenAdd}
          sx={{ borderRadius: 1.5 }}
        >
          Register Table
        </Button>
      </Box>

      <StateBox loading={tables.loading} error={tables.error} empty={!rows.length}>
        <Paper variant="outlined" sx={{ borderRadius: 2, overflow: 'hidden' }}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell sx={{ bgcolor: '#F8FAFC', fontWeight: 'bold' }}>Schema</TableCell>
                <TableCell sx={{ bgcolor: '#F8FAFC', fontWeight: 'bold' }}>Table Name</TableCell>
                <TableCell sx={{ bgcolor: '#F8FAFC', fontWeight: 'bold' }}>Status</TableCell>
                <TableCell align="right" sx={{ bgcolor: '#F8FAFC', fontWeight: 'bold' }}>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.map((row) => (
                <TableRow key={row.id} hover>
                  <TableCell>{row.schema_name}</TableCell>
                  <TableCell fontWeight={500}>{row.table_name}</TableCell>
                  <TableCell>
                    <StatusChip value={row.is_active ? "active" : "inactive"} />
                  </TableCell>
                  <TableCell align="right">
                    <IconButton size="small" onClick={() => handleToggleActive(row)} color={row.is_active ? "warning" : "success"}>
                      {row.is_active ? <CancelOutlined fontSize="small" /> : <CheckCircleOutline fontSize="small" />}
                    </IconButton>
                    <IconButton size="small" color="error" onClick={() => handleDelete(row.id)}>
                      <DeleteOutline fontSize="small" />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Paper>
      </StateBox>

      <Dialog open={openAdd} onClose={() => setOpenAdd(false)} maxWidth="sm" fullWidth PaperProps={{ sx: { borderRadius: 2 } }}>
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <StorageOutlined color="primary" />
          Register New Table
        </DialogTitle>
        <DialogContent dividers>
          <Stack spacing={3} sx={{ mt: 1 }}>
            <Typography variant="body2" color="text.secondary">
              Select a schema and table from <strong>{connectionData.iceberg_catalog_name}</strong> to register in DataGate.
            </Typography>
            
            <FormControl fullWidth size="small">
              <InputLabel>Schema</InputLabel>
              <Select
                value={selectedSchema}
                label="Schema"
                onChange={handleSchemaChange}
                disabled={loadingSchemas}
              >
                {loadingSchemas ? (
                  <MenuItem disabled><CircularProgress size={20} sx={{ mr: 1 }} /> Loading...</MenuItem>
                ) : (
                  schemas.map(s => <MenuItem key={s} value={s}>{s}</MenuItem>)
                )}
              </Select>
            </FormControl>

            <FormControl fullWidth size="small" disabled={!selectedSchema || loadingDiscovery}>
              <InputLabel>Table</InputLabel>
              <Select
                value={selectedTable}
                label="Table"
                onChange={e => setSelectedTable(e.target.value)}
              >
                {loadingDiscovery ? (
                  <MenuItem disabled><CircularProgress size={20} sx={{ mr: 1 }} /> Discovery...</MenuItem>
                ) : (
                  discoveryTables.length === 0 ? (
                    <MenuItem disabled>No tables found</MenuItem>
                  ) : (
                    discoveryTables.map(t => <MenuItem key={t} value={t}>{t}</MenuItem>)
                  )
                )}
              </Select>
            </FormControl>
          </Stack>
        </DialogContent>
        <DialogActions sx={{ p: 2.5 }}>
          <Button onClick={() => setOpenAdd(false)} color="inherit">Cancel</Button>
          <Button 
            variant="contained" 
            onClick={handleRegister} 
            disabled={!selectedTable || adding}
            startIcon={adding ? <CircularProgress size={16} /> : <SaveOutlined />}
          >
            {adding ? "Registering..." : "Register"}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default PlatformConnection;