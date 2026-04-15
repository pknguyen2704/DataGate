import React, { useState, useEffect } from "react";
import {
  Box,
  Typography,
  Paper,
  Grid,
  TextField,
  InputAdornment,
  Collapse,
  Divider,
  IconButton,
  CircularProgress,
  Alert,
} from "@mui/material";
import {
  Search as SearchIcon,
  TableChart as TableIcon,
  KeyboardArrowDown as ExpandIcon,
  KeyboardArrowUp as CollapseIcon,
  FilterList as FilterIcon,
  Refresh as RefreshIcon,
  Dns as DbIcon,
} from "@mui/icons-material";
import { servicesApi } from "~/apis/services";
import TrinoIcon from "~/assets/images/Trino.svg";

const Explore = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [expandedDb, setExpandedDb] = useState(null);
  const [services, setServices] = useState([]);
  const [tablesMap, setTablesMap] = useState({});
  const [loading, setLoading] = useState(true);
  const [loadingTables, setLoadingTables] = useState({});
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchServices();
  }, []);

  const fetchServices = async () => {
    try {
      setLoading(true);
      const response = await servicesApi.getServices();
      setServices(response.data || []);
      setError(null);
    } catch (err) {
      console.error("Failed to fetch services:", err);
      setError("Could not load databases. Please check connection.");
    } finally {
      setLoading(false);
    }
  };

  const fetchTables = async (serviceId) => {
    if (tablesMap[serviceId]) return; 
    
    try {
      setLoadingTables(prev => ({ ...prev, [serviceId]: true }));
      const response = await servicesApi.getServiceTables(serviceId);
      setTablesMap(prev => ({ ...prev, [serviceId]: response.data || [] }));
    } catch (err) {
      console.error(`Failed to fetch tables for ${serviceId}:`, err);
    } finally {
      setLoadingTables(prev => ({ ...prev, [serviceId]: false }));
    }
  };

  const handleToggleDb = (serviceId) => {
    const isExpanding = expandedDb !== serviceId;
    setExpandedDb(isExpanding ? serviceId : null);
    if (isExpanding) {
      fetchTables(serviceId);
    }
  };

  const getServiceIcon = (type) => {
    if (type?.toLowerCase() === 'trino') {
      return <Box component="img" src={TrinoIcon} sx={{ width: 22, height: 22, objectFit: 'contain' }} />;
    }
    return <DbIcon fontSize="small" />;
  };

  const filteredServices = services.filter(service => {
    const serviceMatches = service.name?.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          service.service_type?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const tables = tablesMap[service.id] || [];
    const tableMatches = tables.some(t => t.table_name?.toLowerCase().includes(searchTerm.toLowerCase()));
    
    return serviceMatches || tableMatches;
  });

  if (loading) return (
    <Box sx={{ display: 'flex', justifyContent: 'center', py: 10 }}>
      <CircularProgress size={32} />
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', gap: 0, height: '100%' }}>
      {/* Internal Navigation Sidebar - Wider */}
      <Box sx={{ 
        width: 320, 
        flexShrink: 0, 
        bgcolor: 'white', 
        p: 3,
        display: 'flex',
        flexDirection: 'column',
        gap: 2,
        boxShadow: 'none'
      }}>
        <Typography variant="h6" sx={{ fontWeight: 800, mb: 1 }}>Databases</Typography>
        
        <TextField
            fullWidth
            size="small"
            placeholder="Filter databases..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon fontSize="small" color="action" />
                </InputAdornment>
              ),
              sx: { bgcolor: '#F8FAFC', border: 'none' }
            }}
          />

        <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
          {services.map(s => (
            <Box 
              key={s.id}
              onClick={() => handleToggleDb(s.id)}
              sx={{ 
                p: 1.5, 
                borderRadius: '4px', 
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: 1.5,
                mb: 0.5,
                bgcolor: expandedDb === s.id ? 'primary.50' : 'transparent',
                color: expandedDb === s.id ? 'primary.main' : 'inherit',
                '&:hover': { bgcolor: expandedDb === s.id ? 'primary.50' : '#F8FAFC' }
              }}
            >
              {getServiceIcon(s.service_type)}
              <Typography variant="body2" fontWeight={expandedDb === s.id ? 700 : 500} noWrap>
                {s.name}
              </Typography>
            </Box>
          ))}
        </Box>
      </Box>

      {/* Main Content Area - White background */}
      <Box sx={{ flexGrow: 1, bgcolor: 'white', p: 4, overflow: 'auto' }}>
        {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}

        <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box>
            <Typography variant="h5" fontWeight="800" sx={{ mb: 0.5 }}>
              {expandedDb ? services.find(s => s.id === expandedDb)?.name : "All Assets"}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {expandedDb ? `Exploring tables in ${services.find(s => s.id === expandedDb)?.service_type}` : "Select a database to browse its tables."}
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <IconButton onClick={fetchServices} size="small">
              <RefreshIcon fontSize="small" />
            </IconButton>
            <IconButton size="small">
              <FilterIcon fontSize="small" />
            </IconButton>
          </Box>
        </Box>

        {/* Tables Grid */}
        <Grid container spacing={2}>
          {expandedDb ? (
            (tablesMap[expandedDb] || [])
                .filter(t => (t.table_name || "").toLowerCase().includes(searchTerm.toLowerCase()))
              .map(table => (
                  <Grid item xs={12} sm={6} md={4} lg={3} key={table.table_name || Math.random()}>
                    <Paper 
                      elevation={0}
                      sx={{ 
                        p: 2, 
                        borderRadius: '4px', 
                        display: 'flex', 
                        alignItems: 'center', 
                        gap: 2,
                        bgcolor: '#F8FAFC',
                        '&:hover': { bgcolor: '#F1F5F9', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.05)' },
                        cursor: 'pointer'
                      }}
                    >
                  <TableIcon fontSize="small" color="primary" sx={{ opacity: 0.7 }} />
                  <Box sx={{ overflow: 'hidden' }}>
                    <Typography variant="body2" fontWeight={700} noWrap>
                      {table.table_name}
                    </Typography>
                    <Typography variant="caption" color="text.secondary" noWrap display="block">
                      {table.schema_name}
                    </Typography>
                  </Box>
                </Paper>
              </Grid>
            ))
          ) : (
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100%', py: 10, color: 'text.secondary' }}>
              <DbIcon sx={{ fontSize: 48, mb: 2, opacity: 0.2 }} />
              <Typography>Please select a database from the sidebar to explore tables.</Typography>
            </Box>
          )}
          
          {expandedDb && !loadingTables[expandedDb] && (tablesMap[expandedDb] || []).length === 0 && (
            <Box sx={{ width: '100%', p: 4, textAlign: 'center' }}>
              <Typography variant="body2" color="text.secondary">No tables found.</Typography>
            </Box>
          )}
          
          {expandedDb && loadingTables[expandedDb] && (
            <Box sx={{ width: '100%', display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress size={24} />
            </Box>
          )}
        </Grid>
      </Box>
    </Box>
  );
};

export default Explore;
