import React, { useState, useEffect } from 'react';
import { 
  Box, Typography, Button, Paper, CircularProgress,
  Divider, IconButton, FormGroup, FormControlLabel, Checkbox, 
  Stack, Grid, List, ListItemButton, ListItemText,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Chip
} from '@mui/material';
import { 
  Refresh as RefreshIcon,
  Lan as IntegrationIcon,
  ArrowBack as BackIcon,
  Delete as DeleteIcon,
  Add as AddIcon
} from '@mui/icons-material';
import { toast } from 'react-toastify';
import { connectionsApi } from '~/apis/connections';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import {
  updateConnection,
  refreshConnectionTables,
} from '~/stores/slices/settingsSlice';
import {
  fetchConnections,
} from '~/stores/slices/exploreSlice/discoverySlice';

const TablesManagement = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const connections = useSelector((state) => state.explore.discovery.connections) || [];
  const status = useSelector((state) => state.explore.discovery.connectionsStatus);
  const isRefreshing = useSelector((state) => state.settings.refreshingByConnection) || {};

  const [integratedTables, setIntegratedTables] = useState([]);
  const [isDiscoveryOpen, setIsDiscoveryOpen] = useState(false);
  
  // Discovery State
  const [discoveredSchemas, setDiscoveredSchemas] = useState([]);
  const [currentSchema, setCurrentSchema] = useState("");
  const [schemaTables, setSchemaTables] = useState([]);
  const [tablesLoading, setTablesLoading] = useState(false);
  const [pendingIntegrated, setPendingIntegrated] = useState([]);

  useEffect(() => {
    dispatch(fetchConnections());
  }, [dispatch]);

  useEffect(() => {
    if (connections.length > 0) {
      setIntegratedTables(connections[0].integrated_tables || []);
    }
  }, [connections]);

  const handleFetchSchemas = async () => {
    if (connections.length === 0) return;
    try {
      const res = await connectionsApi.testConnection(connections[0]);
      if (res.data.schemas) setDiscoveredSchemas(res.data.schemas);
      setIsDiscoveryOpen(true);
    } catch {
      toast.error("Could not fetch schemas");
    }
  };

  const handleFetchTables = async (schema) => {
    setTablesLoading(true);
    setCurrentSchema(schema);
    try {
      const res = await connectionsApi.getRawTables(connections[0].connection_url, schema);
      setSchemaTables(res.data || []);
    } catch {
      toast.error("Could not fetch tables");
    } finally {
      setTablesLoading(false);
    }
  };

  const togglePending = (t) => {
    const full = t.includes('.') ? t : `${currentSchema}.${t}`;
    setPendingIntegrated(prev => prev.includes(full) ? prev.filter(x => x !== full) : [...prev, full]);
  };

  const handleSaveIntegration = async () => {
    try {
      const updatedList = [...new Set([...integratedTables, ...pendingIntegrated])];
      await dispatch(updateConnection({ connectionId: connections[0].id, data: { ...connections[0], integrated_tables: updatedList } })).unwrap();
      setIntegratedTables(updatedList);
      setPendingIntegrated([]);
      setIsDiscoveryOpen(false);
      toast.success("Tables integrated!");
    } catch {
      toast.error("Failed to update tables");
    }
  };

  const handleRemoveTable = async (table) => {
    const newList = integratedTables.filter(t => t !== table);
    try {
      await dispatch(updateConnection({ connectionId: connections[0].id, data: { ...connections[0], integrated_tables: newList } })).unwrap();
      setIntegratedTables(newList);
      toast.success("Removed table");
    } catch {
      toast.error("Remove failed");
    }
  };

  const handleSyncMetadata = async () => {
    if (connections.length === 0) return;
    try {
      await dispatch(refreshConnectionTables(connections[0].id)).unwrap();
      toast.success("Syncing metadata in background...");
    } catch {
      toast.error("Sync failed");
    }
  };

  if (status === 'loading' && connections.length === 0) {
    return <Box sx={{ display: 'flex', justifyContent: 'center', p: 10 }}><CircularProgress /></Box>;
  }

  if (connections.length === 0) {
    return <Box sx={{ p: 4, textAlign: 'center' }}><Typography>Please configure Trino connection first.</Typography></Box>;
  }

  return (
    <Box>
      <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 3 }}>
        <Stack direction="row" alignItems="center" spacing={1}>
          <IconButton onClick={() => navigate('/settings/connection')}><BackIcon /></IconButton>
          <Typography variant="h5" fontWeight="800">Integrated Tables</Typography>
        </Stack>
        <Stack direction="row" spacing={2}>
           <Button 
            variant="outlined" startIcon={<RefreshIcon />} 
            onClick={handleSyncMetadata} disabled={isRefreshing[connections[0]?.id]}
            sx={{ borderRadius: 2 }}
           >
             {isRefreshing[connections[0]?.id] ? 'Refreshing...' : 'Sync Metadata'}
           </Button>
           <Button 
            variant="contained" startIcon={<AddIcon />} 
            onClick={handleFetchSchemas} 
            sx={{ borderRadius: 2, fontWeight: 700 }}
           >
             Add Tables
           </Button>
        </Stack>
      </Stack>

      {isDiscoveryOpen ? (
        <Paper elevation={0} sx={{ p: 3, border: '1px solid #ddd', borderRadius: 3, bgcolor: '#fff' }}>
           <Typography variant="h6" fontWeight="800" sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 1 }}>
             <IntegrationIcon color="primary" /> Selection Mode
           </Typography>
           <Grid container spacing={3} sx={{ minHeight: 400 }}>
             <Grid item xs={4}>
               <Paper variant="outlined" sx={{ borderRadius: 2, bgcolor: '#f8fafc' }}>
                  <Typography variant="caption" sx={{ p: 2, display: 'block', fontWeight: 900 }}>SCHEMAS</Typography>
                  <List dense>
                    {discoveredSchemas.map(s => (
                      <ListItemButton key={s} selected={currentSchema === s} onClick={() => handleFetchTables(s)}>
                        <ListItemText primary={s} />
                      </ListItemButton>
                    ))}
                  </List>
               </Paper>
             </Grid>
             <Grid item xs={8}>
                <Paper variant="outlined" sx={{ p: 2, borderRadius: 2, height: '100%' }}>
                  <Typography variant="caption" sx={{ mb: 2, display: 'block', fontWeight: 900 }}>
                    AVAILABLE TABLES ({pendingIntegrated.length} selected)
                  </Typography>
                  {tablesLoading ? <Box sx={{ display: 'flex', justifyContent: 'center', pt: 10 }}><CircularProgress /></Box> : (
                    <FormGroup sx={{ maxHeight: 400, overflow: 'auto' }}>
                      {schemaTables.map(t => {
                        const full = t.includes('.') ? t : `${currentSchema}.${t}`;
                        const isAlreadyIntegrated = integratedTables.includes(full);
                        return (
                          <FormControlLabel 
                            key={t} 
                            disabled={isAlreadyIntegrated}
                            control={<Checkbox size="small" checked={isAlreadyIntegrated || pendingIntegrated.includes(full)} onChange={() => togglePending(t)} />} 
                            label={<Typography variant="body2">{t} {isAlreadyIntegrated && "(Included)"}</Typography>} 
                          />
                        );
                      })}
                    </FormGroup>
                  )}
                </Paper>
             </Grid>
           </Grid>
           <Box sx={{ mt: 4, display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
              <Button onClick={() => { setIsDiscoveryOpen(false); setPendingIntegrated([]); }}>Cancel</Button>
              <Button variant="contained" onClick={handleSaveIntegration} disabled={pendingIntegrated.length === 0} sx={{ px: 4, fontWeight: 800 }}>Confirm Selection</Button>
           </Box>
        </Paper>
      ) : (
        <TableContainer component={Paper} elevation={0} sx={{ border: '1px solid #eee', borderRadius: 2 }}>
          <Table size="small">
            <TableHead sx={{ bgcolor: '#f8fafc' }}>
              <TableRow>
                <TableCell sx={{ fontWeight: 800 }}>Table Name</TableCell>
                <TableCell sx={{ fontWeight: 800 }}>Schema</TableCell>
                <TableCell sx={{ fontWeight: 800 }}>Status</TableCell>
                <TableCell align="right" sx={{ fontWeight: 800 }}>Action</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {integratedTables.length === 0 ? (
                <TableRow><TableCell colSpan={4} align="center" sx={{ py: 6 }}>No tables integrated yet.</TableCell></TableRow>
              ) : (
                integratedTables.map((fullTableName) => {
                  const [schema, name] = fullTableName.includes('.') ? fullTableName.split('.') : ['', fullTableName];
                  return (
                    <TableRow key={fullTableName} hover>
                      <TableCell sx={{ fontWeight: 600 }}>{name}</TableCell>
                      <TableCell><Chip label={schema} size="small" variant="outlined" /></TableCell>
                      <TableCell><Chip label="Active" size="small" color="success" sx={{ height: 20 }} /></TableCell>
                      <TableCell align="right">
                        <IconButton size="small" color="error" onClick={() => handleRemoveTable(fullTableName)}>
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  );
                })
              )}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );
};

export default TablesManagement;