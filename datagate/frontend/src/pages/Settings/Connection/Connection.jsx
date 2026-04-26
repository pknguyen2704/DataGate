import React, { useState, useEffect } from 'react';
import { 
  Box, Typography, Button, Paper, TextField, Stack, IconButton, InputAdornment, OutlinedInput, Divider, CircularProgress
} from '@mui/material';
import { Save as SaveIcon, Visibility, VisibilityOff } from '@mui/icons-material';
import { toast } from 'react-toastify';
import { connectionsApi } from '~/apis/api';

const Connection = () => {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [trino, setTrino] = useState({ id: null, host_port: '', username: '', password: '', catalog: '' });
  const [catalog, setCatalog] = useState({ id: null, uri: '', credential: '', warehouse: '' });
  const [minio, setMinio] = useState({ id: null, endpoint: '', access_key: '', secret_key: '' });

  const [showTrinoPw, setShowTrinoPw] = useState(false);
  const [showCatalogCred, setShowCatalogCred] = useState(false);
  const [showMinioSecret, setShowMinioSecret] = useState(false);

  useEffect(() => {
    loadConnections();
  }, []);

  const loadConnections = async () => {
    try {
      const res = await connectionsApi.list();
      const list = res.data;
      
      const t = list.find(c => c.conn_type === 'trino');
      if (t && t.config) setTrino({ id: t.id, ...t.config });
      
      const c = list.find(c => c.conn_type === 'iceberg_rest');
      if (c && c.config) setCatalog({ id: c.id, ...c.config });
      
      const m = list.find(c => c.conn_type === 'minio');
      if (m && m.config) setMinio({ id: m.id, ...m.config });
      
    } catch (e) {
      toast.error("Failed to load connections");
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    const payloads = [
      { id: trino.id, name: 'Trino Engine', conn_type: 'trino', config: { host_port: trino.host_port, username: trino.username, password: trino.password, catalog: trino.catalog } },
      { id: catalog.id, name: 'Iceberg REST Catalog', conn_type: 'iceberg_rest', config: { uri: catalog.uri, credential: catalog.credential, warehouse: catalog.warehouse } },
      { id: minio.id, name: 'MinIO Storage', conn_type: 'minio', config: { endpoint: minio.endpoint, access_key: minio.access_key, secret_key: minio.secret_key } }
    ];

    try {
      for (const p of payloads) {
        if (p.id) {
          await connectionsApi.update(p.id, { name: p.name, description: '', conn_type: p.conn_type, config: p.config, is_active: true });
        } else {
          // Only create if at least one field has data
          const hasData = Object.values(p.config).some(v => v !== '');
          if (hasData) {
            await connectionsApi.create({ name: p.name, description: '', conn_type: p.conn_type, config: p.config, is_active: true });
          }
        }
      }
      toast.success("Configurations saved successfully!");
      loadConnections();
    } catch (e) {
      toast.error("Failed to save configurations");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <Box sx={{ display: 'flex', justifyContent: 'center', p: 10 }}><CircularProgress /></Box>;
  }

  return (
    <Box sx={{ maxWidth: 800 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight="900" mb={1}>Connection Management</Typography>
        <Typography variant="body1" color="text.secondary">
          Configure your core infrastructure connections: Query Engine, Catalog, and Object Storage.
        </Typography>
      </Box>

      <Stack spacing={4}>
        {/* QUERY ENGINE */}
        <Paper className="glass-card" elevation={0} sx={{ p: 4, borderRadius: 2 }}>
          <Typography variant="h6" fontWeight="800" mb={3} color="primary.light">
            1. Query Engine (Trino)
          </Typography>
          <Stack spacing={2.5}>
            <Stack direction={{ xs: 'column', md: 'row' }} spacing={2}>
              <TextField 
                fullWidth label="Host:Port" value={trino.host_port} placeholder="localhost:8080"
                onChange={(e) => setTrino({...trino, host_port: e.target.value})}
              />
              <TextField 
                fullWidth label="Catalog" value={trino.catalog} placeholder="iceberg"
                onChange={(e) => setTrino({...trino, catalog: e.target.value})}
              />
            </Stack>
            <Stack direction={{ xs: 'column', md: 'row' }} spacing={2}>
              <TextField 
                fullWidth label="Username" value={trino.username} 
                onChange={(e) => setTrino({...trino, username: e.target.value})}
              />
              <OutlinedInput 
                fullWidth placeholder="Password (Optional)" type={showTrinoPw ? 'text' : 'password'}
                value={trino.password} onChange={(e) => setTrino({...trino, password: e.target.value})}
                endAdornment={
                  <InputAdornment position="end">
                    <IconButton onClick={() => setShowTrinoPw(!showTrinoPw)} edge="end">
                      {showTrinoPw ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                }
              />
            </Stack>
          </Stack>
        </Paper>

        {/* CATALOG */}
        <Paper className="glass-card" elevation={0} sx={{ p: 4, borderRadius: 2 }}>
          <Typography variant="h6" fontWeight="800" mb={3} color="primary.light">
            2. Metadata Catalog (Iceberg REST)
          </Typography>
          <Stack spacing={2.5}>
            <TextField 
              fullWidth label="URI Endpoint" value={catalog.uri} placeholder="http://localhost:8181"
              onChange={(e) => setCatalog({...catalog, uri: e.target.value})}
            />
            <Stack direction={{ xs: 'column', md: 'row' }} spacing={2}>
              <TextField 
                fullWidth label="Warehouse" value={catalog.warehouse} placeholder="s3://lakehouse/"
                onChange={(e) => setCatalog({...catalog, warehouse: e.target.value})}
              />
            </Stack>
          </Stack>
        </Paper>

        {/* STORAGE */}
        <Paper className="glass-card" elevation={0} sx={{ p: 4, borderRadius: 2 }}>
          <Typography variant="h6" fontWeight="800" mb={3} color="primary.light">
            3. Object Storage (MinIO)
          </Typography>
          <Stack spacing={2.5}>
            <TextField 
              fullWidth label="Endpoint URL" value={minio.endpoint} placeholder="http://localhost:9000"
              onChange={(e) => setMinio({...minio, endpoint: e.target.value})}
            />
            <Stack direction={{ xs: 'column', md: 'row' }} spacing={2}>
              <TextField 
                fullWidth label="Access Key" value={minio.access_key} 
                onChange={(e) => setMinio({...minio, access_key: e.target.value})}
              />
              <OutlinedInput 
                fullWidth placeholder="Secret Key" type={showMinioSecret ? 'text' : 'password'}
                value={minio.secret_key} onChange={(e) => setMinio({...minio, secret_key: e.target.value})}
                endAdornment={
                  <InputAdornment position="end">
                    <IconButton onClick={() => setShowMinioSecret(!showMinioSecret)} edge="end">
                      {showMinioSecret ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                }
              />
            </Stack>
          </Stack>
        </Paper>

        <Box sx={{ pt: 2, pb: 4 }}>
          <Button 
            variant="contained" 
            size="large" 
            startIcon={<SaveIcon />} 
            onClick={handleSave}
            disabled={saving}
            sx={{ py: 1.5, px: 4, borderRadius: 2, fontWeight: 800 }}
          >
            {saving ? 'Saving...' : 'Save All Configurations'}
          </Button>
        </Box>
      </Stack>
    </Box>
  );
};

export default Connection;
