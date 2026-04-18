import React, { useState, useEffect } from 'react';
import { 
  Box, Typography, Button, Paper, Table, TableBody, 
  TableCell, TableContainer, TableHead, TableRow, 
  Chip, TextField, Dialog, DialogTitle,
  DialogContent, DialogActions, Select, MenuItem, CircularProgress, Alert,
  Checkbox, FormControlLabel, FormGroup, Divider, List, ListItemText,
  ListItemButton, IconButton, Tooltip,
  Stepper, Step, StepLabel, Grid, Card, CardActionArea, CardContent,
  InputAdornment, OutlinedInput
} from '@mui/material';
import { 
  Search as SearchIcon, 
  Add as AddIcon,
  CheckCircle as SuccessIcon,
  Refresh as RefreshIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
  Close as CloseIcon,
  Storage as StorageIcon
} from '@mui/icons-material';
import { toast } from 'react-toastify';
import { servicesApi } from '~/apis/services';
import { useDispatch, useSelector } from 'react-redux';
import {
  createService,
  deleteService,
  fetchServices,
  refreshServiceTables,
  updateService,
} from '~/stores/slices/servicesSlice';

import trinoIcon from '~/assets/images/trino.svg';

const ServiceList = () => {
  const dispatch = useDispatch();
  const services = useSelector((state) => state.services.services);
  const servicesStatus = useSelector((state) => state.services.servicesStatus);
  const refreshingServices = useSelector((state) => state.services.refreshingByService);
  
  const [open, setOpen] = useState(false);
  const [activeStep, setActiveStep] = useState(0);
  const [testing, setTesting] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [editingServiceId, setEditingServiceId] = useState(null);

  const [discoveredSchemas, setDiscoveredSchemas] = useState([]);
  const [currentSchema, setCurrentSchema] = useState("");
  const [schemaTables, setSchemaTables] = useState([]);
  const [tablesLoading, setTablesLoading] = useState(false);
  const [integratedTables, setIntegratedTables] = useState([]);

  const steps = ['Select Service Type', 'Configure Service', 'Connection Details', 'Integrated Tables'];

  const SERVICE_TYPES = [
    { 
      id: 'trino', 
      name: 'Trino', 
      icon: trinoIcon,
      fields: [
        { name: 'username', label: 'Username', required: true },
        { name: 'password', label: 'Password', type: 'password' },
        { name: 'host_port', label: 'Host And Port', required: true, placeholder: 'localhost:8080' },
        { name: 'catalog', label: 'Catalog', placeholder: 'hive' },
      ],
      urlBuilder: (data) => `trino://${data.username}${data.password ? ':' + data.password : ''}@${data.host_port}/${data.catalog || ''}`
    },
    { 
      id: 'postgres', 
      name: 'PostgreSQL', 
      icon: null, // Placeholder
      fields: [
        { name: 'username', label: 'Username', required: true },
        { name: 'password', label: 'Password', type: 'password' },
        { name: 'host_port', label: 'Host And Port', required: true, placeholder: 'localhost:5432' },
        { name: 'database', label: 'Database', required: true },
      ],
      urlBuilder: (data) => `postgresql://${data.username}:${data.password}@${data.host_port}/${data.database}`
    }
  ];

  const [isTestSuccessful, setIsTestSuccessful] = useState(false);

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    service_type: '',
    connection_url: '',
  });
  const [connectionFields, setConnectionFields] = useState({});

  useEffect(() => {
    if (servicesStatus === "idle") {
      dispatch(fetchServices());
    }
  }, [dispatch, servicesStatus]);

  const handleOpenAdd = () => {
    setEditingServiceId(null);
    setActiveStep(0);
    setFormData({ 
      name: '', 
      description: '', 
      service_type: '', 
      connection_url: '',
    });
    setConnectionFields({});
    setIntegratedTables([]);
    setIsTestSuccessful(false);
    setDiscoveredSchemas([]);
    setCurrentSchema("");
    setSchemaTables([]);
    setOpen(true);
  };

  const handleOpenEdit = (service) => {
    setEditingServiceId(service.id);
    setActiveStep(1);
    setFormData({
      name: service.name,
      description: service.description || '',
      service_type: service.service_type,
      connection_url: service.connection_url,
    });
    setConnectionFields({}); // Fields not easily restorable from flat URL without parser
    setIntegratedTables(service.integrated_tables || []);
    setIsTestSuccessful(true);
    setOpen(true);
    setDiscoveredSchemas([]);
    setCurrentSchema("");
    setSchemaTables([]);
  };

  const handleNext = () => {
    if (activeStep === 2) {
      // Build URL based on service type
      const typeCfg = SERVICE_TYPES.find(t => t.id === formData.service_type);
      const url = typeCfg ? typeCfg.urlBuilder(connectionFields) : formData.connection_url;
      const newFormData = { ...formData, connection_url: url };
      setFormData(newFormData);
      handleTest(newFormData);
    }
    setActiveStep((prev) => prev + 1);
  };

  const handleBack = () => setActiveStep((prev) => prev - 1);

  const handleTest = async (payloadOverride = null) => {
    setTesting(true);
    try {
      const typeCfg = SERVICE_TYPES.find(t => t.id === formData.service_type);
      const url = typeCfg ? typeCfg.urlBuilder(connectionFields) : formData.connection_url;
      const payload = payloadOverride || { ...formData, connection_url: url };
      
      const res = await servicesApi.testConnection(payload);
      if (res.data.status === 'success') {
        toast.success("Connection successful!");
        setIsTestSuccessful(true);
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
    setTablesLoading(true);
    setCurrentSchema(schema);
    try {
      const res = await servicesApi.getSchemaTablesRaw(formData.service_type, formData.connection_url, schema);
      setSchemaTables(res.data);
    } catch {
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
      const typeCfg = SERVICE_TYPES.find(t => t.id === formData.service_type);
      const url = typeCfg ? typeCfg.urlBuilder(connectionFields) : formData.connection_url;
      const data = { 
        ...formData,
        connection_url: url,
        integrated_tables: integratedTables 
      };
      
      if (editingServiceId) {
        await dispatch(updateService({ serviceId: editingServiceId, data })).unwrap();
        toast.success("Service updated successfully!");
      } else {
        await dispatch(createService(data)).unwrap();
        toast.success("Service integrated successfully!");
      }
      setOpen(false);
      dispatch(fetchServices());
    } catch (err) {
      toast.error("Failed to save: " + (err.message || err));
    }
  };

  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [serviceToDelete, setServiceToDelete] = useState(null);

  const handleRefresh = async (serviceId) => {
    try {
      await dispatch(refreshServiceTables(serviceId)).unwrap();
      toast.success("Tables synchronized!");
      dispatch(fetchServices());
    } catch (err) {
      toast.error("Sync failed: " + (err.message || err));
    }
  };

  const handleDelete = async () => {
    if (!serviceToDelete) return;
    try {
      await dispatch(deleteService(serviceToDelete.id)).unwrap();
      toast.success(`Service "${serviceToDelete.name}" deleted`);
      dispatch(fetchServices());
    } catch {
      toast.error("Failed to delete service");
    } finally {
      setDeleteConfirmOpen(false);
    }
  };

  return (
    <Box sx={{ p: 4, bgcolor: '#fdfdfd', minHeight: '100vh' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h4" fontWeight="800" color="primary.main">Database Services</Typography>
          <Typography variant="body1" color="text.secondary">Manage your data source connections and table integrations.</Typography>
        </Box>
        <Button 
          variant="contained" 
          startIcon={<AddIcon />} 
          onClick={handleOpenAdd}
          sx={{ borderRadius: 1.5, px: 4, py: 1.5, textTransform: 'none', fontWeight: 700, boxShadow: 1 }}
        >
          Add New Service
        </Button>
      </Box>

      <TableContainer component={Paper} elevation={0} sx={{ borderRadius: 2, border: '1px solid #eee' }}>
        <Table>
          <TableHead sx={{ bgcolor: '#f8f9fa' }}>
            <TableRow>
              <TableCell sx={{ fontWeight: 800, color: 'text.secondary' }}>SERVICE NAME</TableCell>
              <TableCell sx={{ fontWeight: 800, color: 'text.secondary' }}>TABLES</TableCell>
              <TableCell sx={{ fontWeight: 800, color: 'text.secondary' }}>STATUS</TableCell>
              <TableCell align="right" sx={{ fontWeight: 800, color: 'text.secondary' }}>ACTIONS</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {servicesStatus === "loading" ? (
              <TableRow><TableCell colSpan={4} align="center" sx={{ py: 10 }}><CircularProgress /></TableCell></TableRow>
            ) : services.map((service) => (
              <TableRow key={service.id} hover sx={{ '&:last-child td, &:last-child th': { border: 0 } }}>
                <TableCell sx={{ fontWeight: 700 }}>{service.name}</TableCell>
                <TableCell><Chip label={`${service.integrated_tables?.length || 0} integrated`} size="small" variant="outlined" sx={{ fontWeight: 600 }} /></TableCell>
                <TableCell><Chip label="Active" color="success" size="small" sx={{ fontWeight: 700, borderRadius: '6px' }} /></TableCell>
                <TableCell align="right">
                  <Tooltip title="Edit">
                    <IconButton size="small" onClick={() => handleOpenEdit(service)} sx={{ color: 'info.main' }}><EditIcon fontSize="small" /></IconButton>
                  </Tooltip>
                  <Tooltip title="Sync">
                    <IconButton 
                      size="small" 
                      onClick={() => handleRefresh(service.id)}
                      disabled={refreshingServices[service.id]}
                      sx={{ color: 'primary.main', mx: 1 }}
                    >
                      {refreshingServices[service.id] ? <CircularProgress size={16} /> : <RefreshIcon fontSize="small" />}
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Delete">
                    <IconButton size="small" onClick={() => {setServiceToDelete(service); setDeleteConfirmOpen(true);}} sx={{ color: 'error.main' }}><DeleteIcon fontSize="small" /></IconButton>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Multi-step Dialog */}
      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="md" fullWidth PaperProps={{ sx: { borderRadius: 2 } }}>
        <DialogTitle sx={{ p: 3, borderBottom: '1px solid #eee' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
            <Typography variant="caption" color="text.secondary" fontWeight="600">Database Services</Typography>
            <Typography variant="caption" color="text.secondary">/</Typography>
            <Typography variant="caption" color="primary" fontWeight="600">{editingServiceId ? 'Edit Service' : 'Add New Service'}</Typography>
          </Box>
          <Typography variant="h5" fontWeight="800">
            {activeStep === 0 && "Select Service Type"}
            {activeStep === 1 && "Configure Service"}
            {activeStep === 2 && "Connection Details"}
          </Typography>
        </DialogTitle>

        <DialogContent sx={{ p: 4 }}>
          <Stepper activeStep={activeStep} sx={{ mb: 6 }}>
            {steps.map((label) => (
              <Step key={label}>
                <StepLabel sx={{ '& .MuiStepLabel-label': { fontSize: '0.75rem', fontWeight: 600 } }}>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>

          {activeStep === 0 && (
            <Box>
              <Grid container spacing={3}>
                {SERVICE_TYPES.map((type) => (
                  <Grid item xs={3} key={type.id}>
                    <Card 
                      variant="outlined" 
                      sx={{ 
                        borderRadius: 2, border: '2px solid', 
                        borderColor: formData.service_type === type.id ? 'primary.main' : '#eee',
                        bgcolor: formData.service_type === type.id ? '#f0f7ff' : 'white',
                        position: 'relative'
                      }}
                    >
                      <CardActionArea onClick={() => setFormData({...formData, service_type: type.id})} sx={{ p: 3, textAlign: 'center' }}>
                        <SuccessIcon sx={{ position: 'absolute', top: 8, right: 8, color: 'primary.main', display: formData.service_type === type.id ? 'block' : 'none' }} fontSize="small" />
                        <Box sx={{ height: 48, mb: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                          {type.icon ? <img src={type.icon} alt={type.name} style={{ height: '100%' }} /> : <StorageIcon fontSize="large" />}
                        </Box>
                        <Typography variant="subtitle2" fontWeight="700">{type.name}</Typography>
                      </CardActionArea>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </Box>
          )}

          {activeStep === 1 && (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
              <Box>
                <Typography variant="subtitle2" fontWeight="700" mb={1}>Service Name *</Typography>
                <TextField 
                  fullWidth size="small" placeholder="Service Name"
                  value={formData.name} onChange={(e) => setFormData({...formData, name: e.target.value})}
                  sx={{ '& .MuiOutlinedInput-root': { borderRadius: 1.5 } }}
                />
              </Box>
              <Box>
                <Typography variant="subtitle2" fontWeight="700" mb={1}>Description</Typography>
                <TextField 
                  fullWidth multiline rows={8} placeholder="Description"
                  value={formData.description} onChange={(e) => setFormData({...formData, description: e.target.value})}
                  sx={{ '& .MuiOutlinedInput-root': { borderRadius: 1.5 } }}
                />
              </Box>
            </Box>
          )}

          {activeStep === 2 && (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
              {SERVICE_TYPES.find(t => t.id === formData.service_type)?.fields.map((field) => (
                <Box key={field.name}>
                  <Typography variant="subtitle2" fontWeight="700" mb={1}>{field.label} {field.required && '*'}</Typography>
                  {field.type === 'select' ? (
                    <Select 
                      fullWidth size="small" 
                      value={connectionFields[field.name] || ''}
                      onChange={(e) => setConnectionFields({...connectionFields, [field.name]: e.target.value})}
                      sx={{ borderRadius: 1.5 }}
                    >
                      {field.options.map(opt => <MenuItem key={opt.value} value={opt.value}>{opt.label}</MenuItem>)}
                    </Select>
                  ) : field.type === 'password' ? (
                    <OutlinedInput 
                      fullWidth size="small" type={showPassword ? 'text' : 'password'}
                      value={connectionFields[field.name] || ''}
                      onChange={(e) => setConnectionFields({...connectionFields, [field.name]: e.target.value})}
                      endAdornment={
                        <InputAdornment position="end">
                          <IconButton onClick={() => setShowPassword(!showPassword)} edge="end" size="small">
                            {showPassword ? <VisibilityOffIcon fontSize="small" /> : <VisibilityIcon fontSize="small" />}
                          </IconButton>
                        </InputAdornment>
                      }
                      sx={{ borderRadius: 1.5 }}
                    />
                  ) : (
                    <TextField 
                      fullWidth size="small" placeholder={field.placeholder}
                      value={connectionFields[field.name] || ''} 
                      onChange={(e) => setConnectionFields({...connectionFields, [field.name]: e.target.value})}
                      sx={{ '& .MuiOutlinedInput-root': { borderRadius: 1.5 } }}
                    />
                  )}
                </Box>
              ))}

              <Paper variant="outlined" sx={{ p: 2, borderRadius: 1.5, display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 2 }}>
                <Typography variant="body2" color="text.secondary">Test your connections before creating the service</Typography>
                <Button variant="outlined" size="small" onClick={() => handleTest()} disabled={testing} sx={{ textTransform: 'none', borderRadius: 1.5 }}>
                  {testing ? <CircularProgress size={20} /> : "Test Connection"}
                </Button>
              </Paper>
            </Box>
          )}
          {activeStep === 3 && (
            <Box>
              {discoveredSchemas.length === 0 && !testing && (
                <Alert severity="warning" sx={{ mb: 3, borderRadius: 2 }}>Please test connection successfully to fetch tables.</Alert>
              )}
              {discoveredSchemas.length > 0 && (
                <Box sx={{ display: 'flex', gap: 3, height: 400 }}>
                  <Paper variant="outlined" sx={{ width: 220, overflow: 'auto', borderRadius: 2 }}>
                    <List dense>
                      {discoveredSchemas.map(s => (
                        <ListItemButton key={s} selected={currentSchema === s} onClick={() => handleFetchTables(s)} sx={{ borderRadius: 1.5, mx: 1, my: 0.5 }}>
                          <ListItemText primary={s} slotProps={{ primary: { fontSize: '0.8rem', fontWeight: currentSchema === s ? 700 : 400 } }} />
                        </ListItemButton>
                      ))}
                    </List>
                  </Paper>
                  <Paper variant="outlined" sx={{ flexGrow: 1, overflow: 'auto', p: 3, borderRadius: 2 }}>
                    {tablesLoading ? <Box sx={{ display: 'flex', justifyContent: 'center', pt: 10 }}><CircularProgress /></Box> : (
                      <Box>
                        <Typography variant="subtitle2" fontWeight="800" mb={2}>{currentSchema ? `Tables in ${currentSchema}` : 'Select Schema'}</Typography>
                        <FormGroup>
                          {schemaTables.map(t => (
                            <FormControlLabel 
                              key={t} 
                              control={<Checkbox size="small" checked={integratedTables.includes(`${currentSchema}.${t}`)} onChange={() => toggleTableSelection(t)} />} 
                              label={<Typography variant="body2" fontWeight="500">{t}</Typography>} 
                            />
                          ))}
                        </FormGroup>
                      </Box>
                    )}
                  </Paper>
                </Box>
              )}
            </Box>
          )}
        </DialogContent>

        <DialogActions sx={{ p: 3, borderTop: '1px solid #eee', justifyContent: 'space-between' }}>
          <Button onClick={() => setOpen(false)} sx={{ color: 'text.secondary', fontWeight: 600 }}>Cancel</Button>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button disabled={activeStep === 0} onClick={handleBack} sx={{ fontWeight: 600 }}>Back</Button>
            {activeStep < steps.length - 1 ? (
              <Button variant="contained" onClick={handleNext} disabled={(activeStep === 1 && !formData.name) || (activeStep === 2 && !isTestSuccessful)} sx={{ borderRadius: 1.5, px: 4, fontWeight: 700 }}>Next</Button>
            ) : (
              <Button variant="contained" onClick={handleSave} sx={{ borderRadius: 1.5, px: 4, fontWeight: 700 }}>Finish</Button>
            )}
          </Box>
        </DialogActions>
      </Dialog>

      {/* Delete Dialog */}
      <Dialog open={deleteConfirmOpen} onClose={() => setDeleteConfirmOpen(false)} PaperProps={{ sx: { borderRadius: 2 } }}>
        <DialogTitle sx={{ fontWeight: 800 }}>Delete Service</DialogTitle>
        <DialogContent>
          <Typography color="text.secondary">Are you sure you want to delete "<strong>{serviceToDelete?.name}</strong>"? This action cannot be undone.</Typography>
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={() => setDeleteConfirmOpen(false)}>Cancel</Button>
          <Button variant="contained" color="error" onClick={handleDelete} sx={{ borderRadius: 1.5 }}>Delete</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ServiceList;
