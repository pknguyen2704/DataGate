import React, { useState, useEffect } from 'react';
import { 
  Box, Typography, Button, Paper, Table, TableBody, 
  TableCell, TableContainer, TableHead, TableRow, 
  Chip, TextField, InputAdornment, Dialog, DialogTitle,
  DialogContent, DialogActions, FormControl, InputLabel,
  Select, MenuItem, CircularProgress, Alert,
  Checkbox, FormControlLabel, FormGroup, Divider, List, ListItem, ListItemText,
  ListItemButton, ListItemIcon, IconButton, Tooltip
} from '@mui/material';
import { 
  Search as SearchIcon, 
  Add as AddIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  Refresh as RefreshIcon,
  Storage as StorageIcon,
  Delete as DeleteIcon,
  Edit as EditIcon
} from '@mui/icons-material';
import { toast } from 'react-toastify';
import { servicesApi } from '~/apis/services';

const ServiceList = () => {
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const [testResult, setTestResult] = useState(null);
  const [testing, setTesting] = useState(false);
  
  const [discoveredSchemas, setDiscoveredSchemas] = useState([]);
  const [currentSchema, setCurrentSchema] = useState("");
  const [schemaTables, setSchemaTables] = useState([]);
  const [tablesLoading, setTablesLoading] = useState(false);
  const [integratedTables, setIntegratedTables] = useState([]);
  const [editingServiceId, setEditingServiceId] = useState(null);

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    service_type: 'trino',
    connection_url: '',
  });

  const fetchServices = async () => {
    setLoading(true);
    try {
      const res = await servicesApi.getServices();
      setServices(res.data);
    } catch (err) {
      toast.error("Failed to fetch services");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchServices(); }, []);

  const handleOpenAdd = () => {
    setEditingServiceId(null);
    setFormData({ name: '', service_type: 'trino', connection_url: '' });
    setIntegratedTables([]);
    setDiscoveredSchemas([]);
    setOpen(true);
  };

  const handleOpenEdit = (service) => {
    setEditingServiceId(service.id);
    setFormData({
      name: service.name,
      service_type: service.service_type,
      connection_url: service.connection_url
    });
    setIntegratedTables(service.integrated_tables || []);
    setOpen(true);
    // Auto test to load schemas
    handleTest();
  };

  const handleTest = async () => {
    setTesting(true);
    setTestResult(null);
    setDiscoveredSchemas([]);
    try {
      const res = await servicesApi.testConnection(editingServiceId ? { ...formData, id: editingServiceId } : formData);
      setTestResult(res.data);
      if (res.data.status === 'success') {
        toast.success("Connection successful!");
        if (res.data.schemas) setDiscoveredSchemas(res.data.schemas);
      } else {
        toast.error("Connection failed: " + res.data.message);
      }
    } catch (err) {
      toast.error("Test error: " + err.message);
    } finally {
      setTesting(false);
    }
  };

  const handleFetchTables = async (schema) => {
    setCurrentSchema(schema);
    setTablesLoading(true);
    try {
      const res = await servicesApi.getSchemaTablesRaw(formData.service_type, formData.connection_url, schema);
      setSchemaTables(res.data);
    } catch (err) {
      toast.error("Failed to fetch tables");
    } finally {
      setTablesLoading(false);
    }
  };

  const toggleTableSelection = (tableName) => {
    const fullPath = `${currentSchema}.${tableName}`;
    setIntegratedTables(prev => 
      prev.includes(fullPath) ? prev.filter(t => t !== fullPath) : [...prev, fullPath]
    );
  };

  const handleSave = async () => {
    try {
      const data = { ...formData, integrated_tables: integratedTables };
      if (editingServiceId) {
        await servicesApi.updateService(editingServiceId, data);
        toast.success("Catalog updated successfully!");
      } else {
        await servicesApi.createService(data);
        toast.success("Catalog integrated successfully!");
      }
      setOpen(false);
      fetchServices();
    } catch (err) {
      toast.error("Failed to save: " + err.message);
    }
  };

  // Delete confirmation state
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [serviceToDelete, setServiceToDelete] = useState(null);

  const [refreshingServices, setRefreshingServices] = useState({});

  const handleRefresh = async (serviceId) => {
    setRefreshingServices(prev => ({ ...prev, [serviceId]: true }));
    try {
      await servicesApi.refreshTables(serviceId);
      toast.success("Tables synchronized and orphans removed!");
      fetchServices();
    } catch (err) {
      toast.error("Sync failed: " + (err.response?.data?.detail || err.message));
    } finally {
      setRefreshingServices(prev => ({ ...prev, [serviceId]: false }));
    }
  };

  const openDeleteConfirm = (service) => {
    setServiceToDelete(service);
    setDeleteConfirmOpen(true);
  };

  const handleDelete = async () => {
    if (!serviceToDelete) return;
    try {
      await servicesApi.deleteService(serviceToDelete.id);
      toast.success(`Catalog "${serviceToDelete.name}" deleted`);
      fetchServices();
    } catch (err) {
      toast.error("Failed to delete catalog");
    } finally {
      setDeleteConfirmOpen(false);
      setServiceToDelete(null);
    }
  };

  return (
    <Box>
       {/* Breadcrumbs Placeholder */}
      <Box sx={{ mb: 2 }}>
        <Typography variant="caption" color="text.secondary">Settings / Databases</Typography>
      </Box>

      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h5" fontWeight="700">Data Sources</Typography>
          <Typography variant="body2" color="text.secondary">Connect and manage your data catalogs.</Typography>
        </Box>
        <Button 
          variant="contained" 
          startIcon={<AddIcon />} 
          onClick={handleOpenAdd}
          sx={{ borderRadius: 2, textTransform: 'none', px: 3 }}
        >
          Add New Catalog
        </Button>
      </Box>

      <TableContainer component={Paper} sx={{ borderRadius: 2 }}>
        <Table>
          <TableHead sx={{ bgcolor: '#F8FAFC' }}>
            <TableRow>
              <TableCell sx={{ fontWeight: 700 }}>Catalog Name</TableCell>
              <TableCell sx={{ fontWeight: 700 }}>Type</TableCell>
              <TableCell sx={{ fontWeight: 700 }}>Tables Integrated</TableCell>
              <TableCell sx={{ fontWeight: 700 }}>Status</TableCell>
              <TableCell align="right" sx={{ fontWeight: 700 }}>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow><TableCell colSpan={5} align="center" sx={{ py: 10 }}><CircularProgress /></TableCell></TableRow>
            ) : services.map((service) => (
              <TableRow key={service.id} hover>
                <TableCell sx={{ fontWeight: 600 }}>{service.name}</TableCell>
                <TableCell sx={{ textTransform: 'uppercase', fontSize: '0.75rem' }}>{service.service_type}</TableCell>
                <TableCell>{service.integrated_tables?.length || 0} tables</TableCell>
                <TableCell>
                  <Chip 
                    label="Active" 
                    size="small" 
                    color="success" 
                    sx={{ borderRadius: 1.5, fontWeight: 700 }}
                  />
                </TableCell>
                <TableCell align="right">
                   <Tooltip title="Edit Connection & Tables">
                     <IconButton color="info" onClick={() => handleOpenEdit(service)}>
                        <EditIcon fontSize="small" />
                     </IconButton>
                   </Tooltip>
                   <Tooltip title="Refresh Tables (Sync with DB)">
                     <IconButton 
                       color="primary" 
                       onClick={() => handleRefresh(service.id)}
                       disabled={refreshingServices[service.id]}
                     >
                        {refreshingServices[service.id] ? <CircularProgress size={20} /> : <RefreshIcon fontSize="small" />}
                     </IconButton>
                   </Tooltip>
                   <IconButton color="error" onClick={() => openDeleteConfirm(service)}>
                      <DeleteIcon fontSize="small" />
                   </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Add Dialog */}
      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ fontWeight: 700 }}>
          {editingServiceId ? `Edit ${formData.name}` : "Connect New Catalog"}
        </DialogTitle>
        <DialogContent dividers>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 1 }}>
             <Box sx={{ display: 'flex', gap: 2 }}>
                <TextField label="Name" fullWidth size="small" value={formData.name} onChange={(e) => setFormData({...formData, name: e.target.value})} />
                <Select size="small" value={formData.service_type} sx={{ minWidth: 120 }} onChange={(e) => setFormData({...formData, service_type: e.target.value})}>
                  <MenuItem value="trino">Trino</MenuItem>
                  <MenuItem value="postgres">Postgres</MenuItem>
                </Select>
             </Box>
             <TextField label="Connection URL" fullWidth size="small" value={formData.connection_url} onChange={(e) => setFormData({...formData, connection_url: e.target.value})} />
             <Button variant="outlined" size="small" onClick={handleTest} disabled={testing}>{testing ? <CircularProgress size={20} /> : "Test Connection"}</Button>
             
             {discoveredSchemas.length > 0 && (
               <Box sx={{ display: 'flex', gap: 1, height: 300 }}>
                  <Paper variant="outlined" sx={{ width: 150, overflow: 'auto' }}>
                    <List dense>
                      {discoveredSchemas.map(s => (
                        <ListItemButton key={s} selected={currentSchema === s} onClick={() => handleFetchTables(s)}>
                          <ListItemText primary={s} primaryTypographyProps={{ fontSize: '0.8rem' }} />
                        </ListItemButton>
                      ))}
                    </List>
                  </Paper>
                  <Paper variant="outlined" sx={{ flexGrow: 1, overflow: 'auto', p: 1 }}>
                    {tablesLoading ? <CircularProgress /> : (
                      <FormGroup>
                        {schemaTables.map(t => (
                          <FormControlLabel 
                            key={t} 
                            control={<Checkbox size="small" checked={integratedTables.includes(`${currentSchema}.${t}`)} onChange={() => toggleTableSelection(t)} />} 
                            label={<Typography variant="body2">{t}</Typography>} 
                          />
                        ))}
                      </FormGroup>
                    )}
                  </Paper>
               </Box>
             )}
          </Box>
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button size="small" onClick={() => setOpen(false)}>Cancel</Button>
          <Button size="small" variant="contained" disabled={integratedTables.length === 0} onClick={handleSave}>
            {editingServiceId ? "Save Changes" : "Integrate"}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteConfirmOpen} onClose={() => setDeleteConfirmOpen(false)}>
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          <Typography>Are you sure you want to delete catalog "<strong>{serviceToDelete?.name}</strong>"? This will remove its tables from the platform.</Typography>
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={() => setDeleteConfirmOpen(false)}>Cancel</Button>
          <Button variant="contained" color="error" onClick={handleDelete}>Delete Anyway</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ServiceList;
