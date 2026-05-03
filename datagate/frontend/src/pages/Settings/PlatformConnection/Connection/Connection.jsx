import React, { useEffect, useMemo, useState } from 'react';
import {
  Box,
  Button,
  Checkbox,
  Chip,
  CircularProgress,
  Divider,
  FormControl,
  Grid,
  IconButton,
  InputLabel,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  MenuItem,
  Paper,
  Select,
  Stack,
  Tab,
  Tabs,
  TextField,
  Typography,
} from '@mui/material';
import {
  ArrowBack as BackIcon,
  Block as DisableIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  PlayArrow as TestIcon,
  Save as SaveIcon,
  TableChart as TableIcon,
} from '@mui/icons-material';
import { useConfirm } from 'material-ui-confirm';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { toast } from 'react-toastify';

import {
  addManagedTables,
  clearConnectionDetail,
  deleteManagedTable,
  disableManagedTable,
  fetchCatalogs,
  fetchConnection,
  fetchManagedTables,
  fetchSchemas,
  fetchRemoteTables,
  createConnection,
  testConnection as testConnectionThunk,
  updateConnection,
} from '~/stores/slices/connectionSlice/connectionSlice';

const emptyForm = {
  name: '',
  description: '',
  trino_host: '',
  trino_port: 8080,
  trino_user: '',
  trino_password: '',
  iceberg_rest_url: '',
  iceberg_catalog_name: 'iceberg',
  minio_endpoint_url: '',
  minio_access_key: '',
  minio_secret_key: '',
  minio_region: 'us-east-1',
};

const tableKey = (schema, table) => `${schema}.${table}`;
const isRouteId = (id) => Boolean(id && id !== 'new' && id !== 'undefined' && id !== 'null');

const Connection = () => {
  const { connectionId } = useParams();
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const confirm = useConfirm();
  const [searchParams, setSearchParams] = useSearchParams();
  const isNew = connectionId === 'new';
  const hasRouteConnectionId = isRouteId(connectionId);
  const {
    catalogs,
    currentConnection,
    detailStatus,
    discoveryStatus,
    managedTables,
    managedTablesStatus,
    remoteTables,
    schemas,
    testStatus,
  } = useSelector((state) => state.connection);

  const [activeTab, setActiveTab] = useState(Number(searchParams.get('tab') || 0));
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);
  const [currentConnectionId, setCurrentConnectionId] = useState(hasRouteConnectionId ? connectionId : null);
  const [catalog, setCatalog] = useState('');
  const [schema, setSchema] = useState('');
  const [selectedTables, setSelectedTables] = useState([]);

  const canManageTables = Boolean(currentConnectionId);
  const canAddSelectedTables = Boolean(currentConnectionId && catalog && schema && selectedTables.length > 0);
  const loading = detailStatus === 'loading';
  const testing = testStatus === 'loading';
  const loadingDiscovery = discoveryStatus === 'loading';
  const loadingRegistered = managedTablesStatus === 'loading';

  useEffect(() => {
    if (hasRouteConnectionId) {
      setCurrentConnectionId(connectionId);
      dispatch(fetchConnection(connectionId));
      dispatch(fetchManagedTables(connectionId));
    } else {
      dispatch(clearConnectionDetail());
      setForm(emptyForm);
      setCurrentConnectionId(null);
    }
  }, [connectionId, dispatch, hasRouteConnectionId]);

  useEffect(() => {
    if (currentConnection) {
      setForm({ ...emptyForm, ...currentConnection, trino_password: '', minio_secret_key: '' });
    }
  }, [currentConnection]);

  useEffect(() => {
    if (canManageTables && activeTab === 1) {
      dispatch(fetchCatalogs(currentConnectionId));
      dispatch(fetchSchemas(currentConnectionId));
      dispatch(fetchManagedTables(currentConnectionId));
    }
  }, [activeTab, canManageTables, currentConnectionId, dispatch]);

  const registeredTableKeys = useMemo(
    () => new Set(managedTables.map((item) => tableKey(item.schema_name, item.table_name))),
    [managedTables],
  );

  useEffect(() => {
    if (activeTab === 1 && currentConnectionId && !catalog) {
      const preferredCatalog = form.iceberg_catalog_name || catalogs[0] || '';
      if (preferredCatalog) {
        setCatalog(preferredCatalog);
      }
    }
  }, [activeTab, catalog, catalogs, currentConnectionId, dispatch, form.iceberg_catalog_name]);

  useEffect(() => {
    if (activeTab !== 1) return;
    if (!schemas.includes(schema)) {
      setSchema('');
      setSelectedTables([]);
    }
  }, [activeTab, schema, schemas]);

  useEffect(() => {
    if (activeTab !== 1 || !currentConnectionId || !schema) return;

    dispatch(fetchRemoteTables({
      connectionId: currentConnectionId,
      schema,
    }));
  }, [activeTab, currentConnectionId, dispatch, schema]);

  useEffect(() => {
    setSelectedTables((prev) => prev.filter((name) => remoteTables.includes(name)));
  }, [remoteTables]);

  const handleFieldChange = (field) => (event) => {
    setForm((prev) => ({ ...prev, [field]: event.target.value }));
  };

  const buildPayload = () => ({
    name: form.name.trim(),
    description: form.description || null,
    trino_host: form.trino_host.trim(),
    trino_port: Number(form.trino_port || 8080),
    trino_user: form.trino_user.trim(),
    trino_password: form.trino_password || null,
    iceberg_rest_url: form.iceberg_rest_url.trim(),
    iceberg_catalog_name: form.iceberg_catalog_name.trim(),
    minio_endpoint_url: form.minio_endpoint_url.trim(),
    minio_access_key: form.minio_access_key.trim(),
    minio_secret_key: form.minio_secret_key || null,
    minio_region: form.minio_region.trim() || 'us-east-1',
  });

  const validateForm = () => {
    const requiredFields = ['name', 'trino_host', 'trino_user', 'iceberg_rest_url', 'iceberg_catalog_name', 'minio_endpoint_url', 'minio_access_key'];
    if (!currentConnectionId) requiredFields.push('minio_secret_key');
    const missing = requiredFields.find((field) => !String(form[field] || '').trim());
    if (missing) {
      toast.error('Please fill all required connection fields');
      return false;
    }
    return true;
  };

  const saveConnection = async () => {
    if (!validateForm()) return null;

    setSaving(true);
    try {
      const payload = buildPayload();
      if (currentConnectionId) {
        if (!payload.trino_password) delete payload.trino_password;
        if (!payload.minio_secret_key) delete payload.minio_secret_key;
      }
      const saved = currentConnectionId
        ? await dispatch(updateConnection({ connectionId: currentConnectionId, data: payload })).unwrap()
        : await dispatch(createConnection(payload)).unwrap();
      setCurrentConnectionId(saved.id);
      setForm((prev) => ({ ...prev, ...saved, trino_password: '', minio_secret_key: '' }));
      toast.success(currentConnectionId ? 'Connection updated' : 'Connection created');
      return saved;
    } catch (error) {
      toast.error(error || 'Failed to save connection');
      return null;
    } finally {
      setSaving(false);
    }
  };

  const testConnection = async (id = currentConnectionId) => {
    if (!id) return false;

    try {
      const response = await dispatch(testConnectionThunk(id)).unwrap();
      toast.success(response?.message || 'Connection test succeeded');
      return true;
    } catch (error) {
      toast.error(error || 'Connection test failed');
      return false;
    }
  };

  const handleTabChange = (event, nextTab) => {
    setActiveTab(nextTab);
    setSearchParams({ tab: nextTab });
  };

  const toggleTable = (name) => {
    setSelectedTables((prev) => (
      prev.includes(name) ? prev.filter((item) => item !== name) : [...prev, name]
    ));
  };

  const addSelectedTables = async () => {
    if (!currentConnectionId || !catalog || !schema) {
      toast.error('Select a schema before adding tables');
      return;
    }

    if (selectedTables.length === 0) {
      toast.error('Select at least one table');
      return;
    }

    try {
      const result = await dispatch(addManagedTables({
        connectionId: currentConnectionId,
        catalog,
        schema,
        tableNames: selectedTables,
      })).unwrap();
      if (result.added > 0) toast.success(`${result.added} table${result.added > 1 ? 's' : ''} added`);
      if (result.skipped > 0) toast.info(`${result.skipped} table${result.skipped > 1 ? 's were' : ' was'} already managed or could not be added`);
      setSelectedTables([]);
    } catch (error) {
      toast.error(error || 'Failed to add tables');
    }
  };

  const disableTable = async (managedTable) => {
    try {
      await dispatch(disableManagedTable({
        connectionId: currentConnectionId,
        tableId: managedTable.id,
      })).unwrap();
      toast.success('Table disabled');
    } catch (error) {
      toast.error(error || 'Failed to disable table');
    }
  };

  const deleteTable = async (managedTable) => {
    try {
      await confirm({
        title: 'Delete table?',
        description: `Delete ${managedTable.table_name}?`,
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
      await dispatch(deleteManagedTable({
        connectionId: currentConnectionId,
        tableId: managedTable.id,
      })).unwrap();
      toast.success('Table deleted');
    } catch (error) {
      toast.error(error || 'Failed to delete table');
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 10 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 2 }}>
        <IconButton onClick={() => navigate('/settings/connection')} size="small">
          <BackIcon />
        </IconButton>
        <Box>
          <Typography variant="h4" fontWeight={900}>{isNew ? 'New Connection' : form.name}</Typography>
          <Typography variant="body2" color="text.secondary">Configure, test, and manage platform tables.</Typography>
        </Box>
      </Box>

      <Paper elevation={0} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: '8px', overflow: 'hidden' }}>
        <Tabs value={activeTab} onChange={handleTabChange} sx={{ borderBottom: 1, borderColor: 'divider', px: 2 }}>
          <Tab label="Connection" icon={<EditIcon fontSize="small" />} iconPosition="start" sx={{ minHeight: 56, fontWeight: 700 }} />
          <Tab label="Managed Tables" icon={<TableIcon fontSize="small" />} iconPosition="start" disabled={!canManageTables} sx={{ minHeight: 56, fontWeight: 700 }} />
        </Tabs>

        {activeTab === 0 && (
          <Box sx={{ p: 3 }}>
            <Grid container spacing={2.5}>
              <Grid item xs={12} md={6}>
                <TextField fullWidth required label="Connection name" value={form.name} onChange={handleFieldChange('name')} />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField fullWidth label="Description" value={form.description || ''} onChange={handleFieldChange('description')} />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField fullWidth required label="Trino host" value={form.trino_host} onChange={handleFieldChange('trino_host')} />
              </Grid>
              <Grid item xs={12} md={3}>
                <TextField fullWidth required type="number" label="Trino port" value={form.trino_port} onChange={handleFieldChange('trino_port')} />
              </Grid>
              <Grid item xs={12} md={3}>
                <TextField fullWidth required label="Trino user" value={form.trino_user} onChange={handleFieldChange('trino_user')} />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField fullWidth type="password" label="Trino password" value={form.trino_password || ''} onChange={handleFieldChange('trino_password')} />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField fullWidth required label="Iceberg catalog name" value={form.iceberg_catalog_name} onChange={handleFieldChange('iceberg_catalog_name')} />
              </Grid>
              <Grid item xs={12}>
                <TextField fullWidth required label="Iceberg REST URL" value={form.iceberg_rest_url} onChange={handleFieldChange('iceberg_rest_url')} />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField fullWidth required label="MinIO endpoint URL" value={form.minio_endpoint_url} onChange={handleFieldChange('minio_endpoint_url')} />
              </Grid>
              <Grid item xs={12} md={3}>
                <TextField fullWidth required label="MinIO access key" value={form.minio_access_key} onChange={handleFieldChange('minio_access_key')} />
              </Grid>
              <Grid item xs={12} md={3}>
                <TextField fullWidth type="password" label="MinIO secret key" value={form.minio_secret_key || ''} onChange={handleFieldChange('minio_secret_key')} />
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField fullWidth label="MinIO region" value={form.minio_region} onChange={handleFieldChange('minio_region')} />
              </Grid>
            </Grid>

            <Stack direction="row" spacing={1.5} sx={{ mt: 3 }}>
              <Button variant="contained" startIcon={<SaveIcon />} disabled={saving || testing} onClick={saveConnection}>
                {saving ? 'Saving...' : isNew ? 'Save Connection' : 'Save Changes'}
              </Button>
              {!isNew && (
                <Button variant="text" startIcon={<TestIcon />} disabled={testing} onClick={() => testConnection()}>
                  Test only
                </Button>
              )}
            </Stack>
          </Box>
        )}

        {activeTab === 1 && (
          <Box sx={{ p: 3 }}>
            <Grid container spacing={3}>
              <Grid item xs={12} lg={5}>
                <Typography variant="subtitle1" fontWeight={800} sx={{ mb: 2 }}>Add tables from platform</Typography>
                <Stack spacing={2}>
                  <TextField fullWidth disabled label="Catalog" value={catalog || form.iceberg_catalog_name || ''} />
                  <FormControl fullWidth disabled={!catalog}>
                    <InputLabel>Schema</InputLabel>
                    <Select
                      label="Schema"
                      value={schema}
                      onChange={(event) => {
                        setSchema(event.target.value);
                        setSelectedTables([]);
                      }}
                    >
                      {schemas.map((item) => <MenuItem value={item} key={item}>{item}</MenuItem>)}
                    </Select>
                  </FormControl>
                </Stack>

                <Paper variant="outlined" sx={{ mt: 2, maxHeight: 360, overflow: 'auto', borderRadius: '8px' }}>
                  {loadingDiscovery ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}><CircularProgress size={28} /></Box>
                  ) : remoteTables.length === 0 ? (
                    <Typography variant="body2" color="text.secondary" sx={{ p: 3 }}>
                      {schema ? 'No tables found in this schema.' : 'Select a schema to load tables.'}
                    </Typography>
                  ) : (
                    <List dense>
                      {remoteTables.map((name) => {
                        const isRegistered = registeredTableKeys.has(tableKey(schema, name));
                        return (
                          <ListItem key={name} disablePadding secondaryAction={isRegistered ? <Chip label="Managed" size="small" /> : null}>
                            <ListItemButton disabled={isRegistered} onClick={() => toggleTable(name)}>
                              <ListItemIcon>
                                <Checkbox edge="start" checked={selectedTables.includes(name)} disabled={isRegistered} tabIndex={-1} />
                              </ListItemIcon>
                              <ListItemText primary={name} />
                            </ListItemButton>
                          </ListItem>
                        );
                      })}
                    </List>
                  )}
                </Paper>

                <Button
                  fullWidth
                  variant="contained"
                  startIcon={<TableIcon />}
                  disabled={!canAddSelectedTables}
                  onClick={addSelectedTables}
                  sx={{ mt: 2 }}
                >
                  Add Selected Tables
                </Button>
              </Grid>

              <Grid item xs={12} lg={7}>
                <Typography variant="subtitle1" fontWeight={800} sx={{ mb: 2 }}>Managed tables</Typography>
                <Paper variant="outlined" sx={{ borderRadius: '8px' }}>
                  {loadingRegistered ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}><CircularProgress size={28} /></Box>
                  ) : managedTables.length === 0 ? (
                    <Typography variant="body2" color="text.secondary" sx={{ p: 3 }}>No tables managed by this platform.</Typography>
                  ) : (
                    <List disablePadding>
                      {managedTables.map((managedTable, index) => (
                        <Box key={managedTable.id}>
                          {index > 0 && <Divider />}
                          <ListItem
                            alignItems="flex-start"
                            secondaryAction={
                              <Stack direction="row" spacing={0.5}>
                                <IconButton size="small" disabled={!managedTable.is_active} onClick={() => disableTable(managedTable)}>
                                  <DisableIcon fontSize="small" />
                                </IconButton>
                                <IconButton size="small" color="error" onClick={() => deleteTable(managedTable)}>
                                  <DeleteIcon fontSize="small" />
                                </IconButton>
                              </Stack>
                            }
                            sx={{ py: 2, pr: 12 }}
                          >
                            <ListItemText
                              primary={
                                <Stack direction="row" spacing={1} alignItems="center">
                                  <Typography fontWeight={800}>
                                    {managedTable.table_name}
                                  </Typography>
                                  <Chip label={managedTable.is_active ? 'Active' : 'Disabled'} size="small" color={managedTable.is_active ? 'success' : 'default'} variant="outlined" />
                                </Stack>
                              }
                              secondary={
                                null
                              }
                            />
                          </ListItem>
                        </Box>
                      ))}
                    </List>
                  )}
                </Paper>
              </Grid>
            </Grid>
          </Box>
        )}
      </Paper>
    </Box>
  );
};

export default Connection;
