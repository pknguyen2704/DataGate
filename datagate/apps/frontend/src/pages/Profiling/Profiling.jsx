import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Tab, Tabs, CircularProgress, Alert, Breadcrumbs,
  Container, Avatar, Chip, Button, Divider
} from '@mui/material';
import {
  Dataset as DatasetIcon,
  Timeline as TimelineIcon,
  WarningAmber as WarningIcon,
  ThumbUpOutlined,
  ThumbDownOutlined,
  StarBorder as StarIcon
} from '@mui/icons-material';
import { Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import { servicesApi } from '../../apis/services';
import { rulesApi } from '../../apis/rules';

import ProfilingDashboard from './ProfilingDashboard/ProfilingDashboard';
import TablePreview from './SampleData/SampleData';

const Profiling = () => {
  const [runs, setRuns] = useState([]);
  const [selectedRun, setSelectedRun] = useState(null);
  const [selectedColumn, setSelectedColumn] = useState(null);
  const [histogramData, setHistogramData] = useState([]);
  const [trendData, setTrendData] = useState([]);
  const [trendMetric, setTrendMetric] = useState('completeness');
  
  const [activeRulesCount, setActiveRulesCount] = useState(0);
  
  const [loading, setLoading] = useState(false);
  const [runLoading, setRunLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const navigate = useNavigate();
  const location = useLocation();
  const currentTab = location.pathname.includes('/preview') ? 1 : 0;

  const fetchRuns = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await profilingApi.getRuns();
      setRuns(response.data);
      if (response.data.length > 0 && !selectedRun) {
        handleSelectRun(response.data[0].id);
      }
    } catch (err) {
      setError("Không thể kết nối tới Backend. Hãy kiểm tra lại Server.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchRuns(); }, []);

  // Sync with Sidebar selection via URL query param
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const tableParam = params.get('table');
    if (tableParam && runs.length > 0) {
      // Find the latest run for this table
      const tableRun = runs.find(r => r.table_name === tableParam);
      if (tableRun) {
        handleSelectRun(tableRun.id);
      }
    }
  }, [location.search, runs]);

  const handleSelectRun = async (runId) => {
    setRunLoading(true);
    try {
      const response = await profilingApi.getRunDetail(runId);
      const tableData = response.data;
      setSelectedRun(tableData);
      
      // Fetch active rules for this table
      const rulesRes = await rulesApi.getRules(tableData.table_name);
      setActiveRulesCount(rulesRes.data.filter(r => r.is_active).length);

      if (tableData.columns.length > 0) {
        handleSelectColumn(tableData.columns[0], tableData.table_name);
      }
    } catch (err) { console.error(err); } finally { setRunLoading(false); }
  };

  const handleSelectColumn = async (column, tableName) => {
    setSelectedColumn(column);
    fetchTrend(tableName, column.column_name, trendMetric);
    try {
      const histRes = await profilingApi.getColumnHistogram(column.id);
      setHistogramData(histRes.data);
    } catch (err) { console.error(err); }
  };

  const fetchTrend = async (tableName, columnName, metric) => {
    try {
      const res = await profilingApi.getTrend(tableName, columnName, metric);
      setTrendData(res.data);
    } catch (err) { console.error(err); }
  };

  const onMetricChange = (e) => {
    const newMetric = e.target.value;
    setTrendMetric(newMetric);
    if (selectedRun && selectedColumn) {
      fetchTrend(selectedRun.table_name, selectedColumn.column_name, newMetric);
    }
  };

  return (
    <Container disableGutters maxWidth={false} sx={{ display: 'flex', flexDirection: 'column', height: (theme) => theme.datagate.mainContentHeight}}>
      {/* Main Content Area */}
      <Box component="main" sx={{ flexGrow: 1, p: { xs: 2, md: 4 }, display: 'flex', flexDirection: 'column', overflow: 'auto', bgcolor: '#F8FAFC' }}>
        {error ? <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert> : null}
        
        {selectedRun ? (
          <Box sx={{ maxWidth: 1400, width: '100%', mx: 'auto' }}>
            {/* Top Navigation Path */}
            <Breadcrumbs separator="/" sx={{ mb: 2, '& .MuiBreadcrumbs-separator': { fontSize: '0.75rem', color: 'text.secondary' } }}>
              <Typography variant="caption" sx={{ textTransform: 'uppercase', color: 'text.secondary', fontWeight: 600, letterSpacing: 0.5 }}>
                {selectedRun.catalog || 'connection1'}
              </Typography>
              <Typography variant="caption" sx={{ textTransform: 'uppercase', color: 'text.secondary', fontWeight: 600, letterSpacing: 0.5 }}>
                {selectedRun.namespace || 'schema'}
              </Typography>
              <Typography variant="caption" sx={{ textTransform: 'uppercase', color: 'text.primary', fontWeight: 700, letterSpacing: 0.5 }}>
                {selectedRun.table_name}
              </Typography>
            </Breadcrumbs>
            
            {/* Title Line */}
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 3, gap: 1.5, flexWrap: 'wrap' }}>
              <Avatar sx={{ bgcolor: '#0EA5E9', width: 44, height: 44 }} variant="rounded">
                <DatasetIcon />
              </Avatar>
              
              <Typography variant="h4" fontWeight="800" sx={{ color: '#0F172A', mr: 2, ml: 1 }}>
                {selectedRun.table_name}
              </Typography>
              
              <Button variant="outlined" size="small" startIcon={<StarIcon />} sx={{ borderRadius: 6, textTransform: 'none', px: 2, color: '#0EA5E9', borderColor: '#0EA5E9' }}>
                Follow
              </Button>
              
              <Box sx={{ flexGrow: 1 }} />
              
              {/* Metadata Badges from active_rules */}
              <Box sx={{ display: 'flex', gap: 1.5, alignItems: 'center' }}>
                <Chip 
                  icon={<WarningIcon />} 
                  label={`${activeRulesCount} Active Rules`} 
                  color={activeRulesCount > 0 ? "primary" : "default"} 
                  variant="outlined" 
                  sx={{ bgcolor: activeRulesCount > 0 ? '#F0F9FF' : 'transparent', fontWeight: 600, borderRadius: 1.5 }} 
                />
                <Tooltip title="View Rules">
                  <IconButton size="small" onClick={() => navigate(`/rules?table=${selectedRun.table_name}`)}>
                    <LayersIcon fontSize="small" color="primary" />
                  </IconButton>
                </Tooltip>
              </Box>
            </Box>

            {/* Metadata Row */}
            <Box sx={{ 
              display: 'flex', flexWrap: 'wrap', gap: { xs: 2, md: 5 }, mb: 3, 
              p: 2, px: 3, border: '1px solid', borderColor: 'divider', borderRadius: 2, bgcolor: 'white' 
            }}>
              <Box>
                <Typography variant="caption" sx={{ color: 'primary.main', fontWeight: 700 }}>Domains</Typography>
                <Box sx={{ mt: 0.5 }}><Chip label="Engineering" size="small" variant="outlined" sx={{ height: 24, fontSize: '0.75rem' }} /></Box>
              </Box>
              <Divider orientation="vertical" flexItem sx={{ display: { xs: 'none', md: 'block' } }} />
              <Box>
                <Typography variant="caption" sx={{ color: 'primary.main', fontWeight: 700 }}>Owners</Typography>
                <Box sx={{ mt: 0.5, display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <Avatar sx={{ width: 24, height: 24, fontSize: '0.7rem', bgcolor: 'primary.main' }}>A</Avatar>
                  <Avatar sx={{ width: 24, height: 24, fontSize: '0.7rem', bgcolor: 'secondary.main' }}>N</Avatar>
                </Box>
              </Box>
              <Divider orientation="vertical" flexItem sx={{ display: { xs: 'none', md: 'block' } }} />
              <Box>
                <Typography variant="caption" sx={{ color: 'primary.main', fontWeight: 700 }}>Tier</Typography>
                <Typography variant="body2" sx={{ mt: 0.5, fontWeight: 600, color: 'text.secondary' }}>Tier 2</Typography>
              </Box>
              <Divider orientation="vertical" flexItem sx={{ display: { xs: 'none', md: 'block' } }} />
              <Box>
                <Typography variant="caption" sx={{ color: 'primary.main', fontWeight: 700 }}>Type</Typography>
                <Typography variant="body2" sx={{ mt: 0.5, fontWeight: 600, color: 'text.secondary' }}>Regular Table</Typography>
              </Box>
              <Divider orientation="vertical" flexItem sx={{ display: { xs: 'none', md: 'block' } }} />
              <Box>
                <Typography variant="caption" sx={{ color: 'primary.main', fontWeight: 700 }}>Volume</Typography>
                <Typography variant="body2" sx={{ mt: 0.5, fontWeight: 600, color: 'text.secondary' }}>
                  {selectedRun.row_count ? selectedRun.row_count.toLocaleString() : '15,420'} Rows
                </Typography>
              </Box>
            </Box>

            {/* Atlan-style tabs via Page Nav */}
            <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
              <Tabs 
                value={currentTab} 
                onChange={(e, v) => navigate(v === 1 ? '/profiling/preview' : '/profiling/dashboard')} 
                indicatorColor="primary" 
                textColor="primary"
                variant="scrollable"
                scrollButtons="auto"
                sx={{
                  minHeight: 48,
                  '& .MuiTab-root': { 
                    textTransform: 'none', 
                    fontWeight: 600, 
                    fontSize: '0.9rem',
                    minWidth: 'auto',
                    px: 3,
                    color: 'text.secondary'
                  },
                  '& .Mui-selected': {
                    color: 'primary.main',
                  }
                }}
              >
                <Tab label="Data Observability" value={0} />
                <Tab label={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    Sample Data
                  </Box>
                } value={1} />
                <Tab disabled label={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    Columns <Chip label={selectedRun.columns?.length || 12} size="small" sx={{ height: 20, fontSize: '0.7rem' }} />
                  </Box>
                } value={2} />
                <Tab disabled label={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    Activity Feeds <Chip label="149" size="small" sx={{ height: 20, fontSize: '0.7rem' }} />
                  </Box>
                } value={3} />
                <Tab disabled label="Queries" value={4} />
                <Tab disabled label="Lineage" value={5} />
                <Tab disabled label="Contract" value={6} />
                <Tab disabled label="Properties" value={7} />
              </Tabs>
            </Box>

            {/* Tab Contents using Routes */}
            <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', bgcolor: 'white', borderRadius: 2, boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.1)', overflow: 'hidden' }}>
              {runLoading ? (
                <Box display="flex" justifyContent="center" alignItems="center" flex={1} py={10}><CircularProgress /></Box>
              ) : (
                <Routes>
                  <Route index element={<Navigate to="dashboard" replace />} />
                  <Route path="dashboard" element={
                    <ProfilingDashboard
                      selectedRun={selectedRun}
                      selectedColumn={selectedColumn}
                      handleSelectColumn={handleSelectColumn}
                      histogramData={histogramData}
                      trendData={trendData}
                      trendMetric={trendMetric}
                      onMetricChange={onMetricChange}
                    />
                  } />
                  <Route path="preview" element={
                    <TablePreview run={selectedRun} />
                  } />
                </Routes>
              )}
            </Box>
          </Box>
        ) : (
           <Box display="flex" justifyContent="center" alignItems="center" flex={1}>
             <Typography color="text.secondary" variant="h6">Select a connection/table from the left pane to view its profile.</Typography>
           </Box>
        )}
      </Box>
    </Container>
  );
};

export default Profiling;