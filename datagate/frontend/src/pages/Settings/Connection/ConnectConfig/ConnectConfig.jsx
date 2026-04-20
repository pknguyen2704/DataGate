import React, { useState, useEffect } from 'react';
import { 
  Box, Typography, Button, Paper, CircularProgress,
  TextField, Divider, IconButton, InputAdornment, OutlinedInput,
  Stack, Avatar
} from '@mui/material';
import { 
  Save as SaveIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
  CheckCircle as SuccessIcon,
  Lan as IntegrationIcon,
  Key as SecurityIcon,
  ArrowBack as BackIcon
} from '@mui/icons-material';
import { toast } from 'react-toastify';
import { connectionsApi } from '~/apis/connections';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import {
  createConnection,
  updateConnection,
} from '~/stores/slices/settingsSlice';
import {
  fetchConnections,
} from '~/stores/slices/exploreSlice/discoverySlice';

const ConnectConfig = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const connections = useSelector((state) => state.explore.discovery.connections) || [];
  const status = useSelector((state) => state.explore.discovery.connectionsStatus);

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    connection_url: '',
  });

  const [trinoFields, setTrinoFields] = useState({
    username: '', password: '', host_port: '', catalog: ''
  });

  const [showPassword, setShowPassword] = useState(false);
  const [testing, setTesting] = useState(false);
  const [isTestSuccessful, setIsTestSuccessful] = useState(false);

  useEffect(() => {
    dispatch(fetchConnections());
  }, [dispatch]);

  useEffect(() => {
    if (connections.length > 0) {
      const conn = connections[0];
      setFormData({
        name: conn.name,
        description: conn.description || '',
        connection_url: conn.connection_url,
      });
      setIsTestSuccessful(true);
    }
  }, [connections]);

  const buildUrl = () => {
    const { username, password, host_port, catalog } = trinoFields;
    if (!username || !host_port) return formData.connection_url;
    return `trino://${username}${password ? ':' + password : ''}@${host_port}/${catalog || ''}`;
  };

  const handleTest = async () => {
    setTesting(true);
    try {
      const url = buildUrl();
      const res = await connectionsApi.testConnection({ ...formData, connection_url: url });
      if (res.data.status === 'success') {
        toast.success("Connection Successful!");
        setIsTestSuccessful(true);
      } else {
        toast.error("Error: " + res.data.message);
        setIsTestSuccessful(false);
      }
    } catch (err) {
      toast.error("Request Failed: " + err.message);
    } finally {
      setTesting(false);
    }
  };

  const handleSave = async () => {
    try {
      const data = { 
          ...formData, 
          connection_url: buildUrl(), 
      };
      if (connections.length > 0) {
        await dispatch(updateConnection({ connectionId: connections[0].id, data })).unwrap();
        toast.success("Connection Updated!");
      } else {
        await dispatch(createConnection(data)).unwrap();
        toast.success("Connection Saved!");
      }
      dispatch(fetchConnections());
    } catch (err) {
      toast.error("Save Failed: " + err.message);
    }
  };

  if (status === 'loading' && connections.length === 0) {
    return <Box sx={{ display: 'flex', justifyContent: 'center', p: 10 }}><CircularProgress /></Box>;
  }

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto' }}>
      <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 3 }}>
        <IconButton onClick={() => navigate('/settings/connection')}><BackIcon /></IconButton>
        <Typography variant="h5" fontWeight="800">Connection Configuration</Typography>
      </Stack>

      <Paper sx={{ p: 4, borderRadius: 3, border: '1px solid #ddd' }} elevation={0}>
        <Stack spacing={4}>
          <Box>
            <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 2, fontWeight: 700 }}>BASIC INFORMATION</Typography>
            <Stack spacing={2.5}>
              <TextField 
                fullWidth label="Connection Name" placeholder="e.g. Trino Production"
                value={formData.name} onChange={(e) => setFormData({...formData, name: e.target.value})}
              />
              <TextField 
                fullWidth multiline rows={2} label="Description"
                value={formData.description} onChange={(e) => setFormData({...formData, description: e.target.value})}
              />
            </Stack>
          </Box>

          <Divider />

          <Box>
            <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 2, fontWeight: 700 }}>CONNECTIVITY (TRINO)</Typography>
            <Stack spacing={2.5}>
              <Stack direction="row" spacing={2}>
                <TextField 
                  fullWidth label="User" value={trinoFields.username} 
                  onChange={(e) => setTrinoFields({...trinoFields, username: e.target.value})}
                />
                <OutlinedInput 
                  fullWidth placeholder="Password (Optional)" type={showPassword ? 'text' : 'password'}
                  value={trinoFields.password} onChange={(e) => setTrinoFields({...trinoFields, password: e.target.value})}
                  endAdornment={
                    <InputAdornment position="end">
                      <IconButton onClick={() => setShowPassword(!showPassword)} edge="end">
                        {showPassword ? <VisibilityOffIcon /> : <VisibilityIcon />}
                      </IconButton>
                    </InputAdornment>
                  }
                />
              </Stack>
              <Stack direction="row" spacing={2}>
                <TextField 
                  fullWidth label="Host:Port" value={trinoFields.host_port} placeholder="localhost:8080"
                  onChange={(e) => setTrinoFields({...trinoFields, host_port: e.target.value})}
                />
                <TextField 
                  fullWidth label="Catalog" value={trinoFields.catalog} placeholder="iceberg"
                  onChange={(e) => setTrinoFields({...trinoFields, catalog: e.target.value})}
                />
              </Stack>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Button variant="outlined" onClick={handleTest} disabled={testing} sx={{ borderRadius: 2 }}>
                  Test Connection
                </Button>
                {isTestSuccessful && (
                  <Typography color="success.main" variant="body2" sx={{ fontWeight: 700, display: 'flex', alignItems: 'center', gap: 0.5 }}>
                    <SuccessIcon fontSize="small" /> Connection Successful
                  </Typography>
                )}
              </Box>
            </Stack>
          </Box>

          <Box sx={{ pt: 2 }}>
            <Button 
                fullWidth variant="contained" size="large" 
                startIcon={<SaveIcon />} onClick={handleSave}
                sx={{ py: 2, borderRadius: 2, fontWeight: 800 }}
              >
              Save Parameters
            </Button>
          </Box>
        </Stack>
      </Paper>
    </Box>
  );
};

export default ConnectConfig;