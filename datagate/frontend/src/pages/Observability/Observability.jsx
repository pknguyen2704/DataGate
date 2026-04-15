import React, { useState, useEffect, useMemo } from 'react';
import { 
  Box, Typography, Grid, Paper, Chip, 
  CircularProgress, Button, IconButton, Card, CardContent, Divider,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Tabs, Tab, Stack, LinearProgress, Breadcrumbs, Link
} from '@mui/material';
import { 
  Refresh as RefreshIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Storage as StorageIcon,
  Timeline as TimelineIcon,
  History as HistoryIcon,
  ChevronRight as ChevronRightIcon,
  Search as SearchIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import { useLocation, useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { 
  fetchSnapshots, fetchVolumeTS, fetchIncidents, 
  fetchSchema, fetchColumnStats 
} from '../../store/slices/observabilitySlice';
import { servicesApi } from '../../apis/services';
import { format, formatDistanceToNow } from 'date-fns';
import { 
  XAxis, YAxis, CartesianGrid, 
  Tooltip as ChartTooltip, ResponsiveContainer, AreaChart, Area 
} from 'recharts';

const Observability = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const dispatch = useDispatch();
  const searchParams = new URLSearchParams(location.search);
  const tableParam = searchParams.get('table');
  const serviceParam = searchParams.get('service');

  const [activeTab, setActiveTab ] = useState(0);
  const [services, setServices] = useState([]);
  const [listLoading, setListLoading] = useState(false);

  // Redux Data
  const snapshots = useSelector(state => state.observability.snapshotsByTable[tableParam] || []);
  const volumeTS = useSelector(state => state.observability.volumeTSByTable[tableParam] || []);
  const incidents = useSelector(state => state.observability.incidentsByTable[tableParam] || []);
  const schemaData = useSelector(state => state.observability.schemasByTable[tableParam] || []);
  const colStats = useSelector(state => state.observability.columnStatsByTable[tableParam] || []);
  const loading = useSelector(state => state.observability.loading);

  const fetchAssetList = async () => {
    setListLoading(true);
    try {
      const res = await servicesApi.getServices();
      setServices(res.data);
    } catch (err) { console.error(err); }
    finally { setListLoading(false); }
  };

  const fetchData = () => {
    if (!tableParam) return;
    dispatch(fetchSnapshots(tableParam));
    dispatch(fetchVolumeTS(tableParam));
    dispatch(fetchIncidents(tableParam));
    dispatch(fetchSchema(tableParam));
    dispatch(fetchColumnStats(tableParam));
  };

  useEffect(() => {
    fetchAssetList();
  }, []);

  useEffect(() => {
    if (tableParam) fetchData();
  }, [tableParam, dispatch]);

  const allTables = useMemo(() => {
    return services.flatMap(s => (s.integrated_tables || []).map(t => ({ 
      name: t, 
      serviceId: s.id, 
      serviceName: s.name,
      type: s.service_type 
    })));
  }, [services]);

  const renderListView = () => (
    <Box sx={{ p: 4, height: '100%', overflow: 'auto' }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight="800" sx={{ mb: 0.5 }}>Data Observability</Typography>
        <Typography variant="body1" color="text.secondary">
          Monitor freshness, volume, and schema health across all your Bronze layer assets.
        </Typography>
      </Box>

      <Paper sx={{ overflow: 'hidden' }}>
        <Box sx={{ p: 2.5, borderBottom: '1px solid', borderColor: 'divider', display: 'flex', justifyContent: 'space-between' }}>
          <Typography variant="h6">Monitored Assets</Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
             <Button size="small" variant="outlined" startIcon={<RefreshIcon />} onClick={fetchAssetList}>Refresh</Button>
          </Box>
        </Box>
        <TableContainer>
          <Table>
            <TableHead sx={{ bgcolor: '#F8FAFC' }}>
              <TableRow>
                <TableCell sx={{ fontWeight: 700 }}>Dataset Name</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Service</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Type</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Health</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Action</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {listLoading ? (
                <TableRow><TableCell colSpan={5} align="center" sx={{ py: 8 }}><CircularProgress size={24} /></TableCell></TableRow>
              ) : allTables.length === 0 ? (
                <TableRow><TableCell colSpan={5} align="center" sx={{ py: 8 }}><Typography color="text.secondary">No assets integrated yet.</Typography></TableCell></TableRow>
              ) : allTables.map((table, i) => (
                <TableRow key={i} hover>
                  <TableCell sx={{ fontWeight: 600 }}>{table.name}</TableCell>
                  <TableCell>{table.serviceName}</TableCell>
                  <TableCell><Chip label={table.type.toUpperCase()} size="small" variant="outlined" sx={{ fontSize: '10px' }} /></TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                       <Box className="status-dot status-healthy" />
                       <Typography variant="body2">Healthy</Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Button 
                      size="small" 
                      onClick={() => navigate(`/observability?table=${table.name}&service=${table.serviceId}`)}
                    >
                      View Monitor
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Box>
  );

  const renderDetailView = () => {
    const latestSnapshot = snapshots[0] || null;
    return (
      <Box sx={{ p: 4, height: '100%', overflow: 'auto' }}>
        <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box>
            <Breadcrumbs sx={{ mb: 0.5 }}>
              <Link underline="hover" color="inherit" onClick={() => navigate('/observability')} sx={{ cursor: 'pointer', fontSize: '0.875rem' }}>Observability</Link>
              <Typography color="text.primary" sx={{ fontSize: '0.875rem', fontWeight: 600 }}>{tableParam}</Typography>
            </Breadcrumbs>
            <Typography variant="h4" sx={{ fontWeight: 800 }}>{tableParam.split('.').pop()}</Typography>
          </Box>
          <Stack direction="row" spacing={1}>
            <Button variant="outlined" startIcon={<SettingsIcon />}>Configure</Button>
            <Button variant="contained" startIcon={<RefreshIcon />} onClick={fetchData}>Snapshot Now</Button>
          </Stack>
        </Box>

        <Grid container spacing={3} sx={{ mb: 3 }}>
          {[
            { label: 'Total Rows', value: latestSnapshot?.total_records?.toLocaleString() || '--', icon: <StorageIcon /> },
            { label: 'Freshness', value: latestSnapshot?.last_updated_time ? formatDistanceToNow(new Date(latestSnapshot.last_updated_time)) + ' ago' : '--', icon: <HistoryIcon />, color: '#10B981' },
            { label: 'Subscribed Rules', value: '4 Rules', icon: <CheckIcon /> },
            { label: 'Open Incidents', value: incidents.filter(i => i.status === 'open').length, icon: <ErrorIcon />, color: incidents.filter(i => i.status === 'open').length > 0 ? '#EF4444' : '#10B981' }
          ].map((item, i) => (
            <Grid item xs={12} sm={6} md={3} key={i}>
              <Paper sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box sx={{ p: 1, borderRadius: '8px', bgcolor: `${item.color || '#2563EB'}15`, color: item.color || '#2563EB' }}>
                  {item.icon}
                </Box>
                <Box>
                  <Typography variant="caption" color="text.secondary" fontWeight={600}>{item.label}</Typography>
                  <Typography variant="h6" fontWeight={700}>{item.value}</Typography>
                </Box>
              </Paper>
            </Grid>
          ))}
        </Grid>

        <Paper sx={{ mb: 3 }}>
          <Tabs value={activeTab} onChange={(e, v) => setActiveTab(v)} sx={{ borderBottom: 1, borderColor: 'divider', px: 2 }}>
            <Tab label="Freshness & Volume" />
            <Tab label="Schema Health" />
            <Tab label="Incidents" />
          </Tabs>
          
          <Box sx={{ p: 3 }}>
            {activeTab === 0 && (
              <Box>
                <Grid container spacing={4}>
                  <Grid item xs={12} lg={6}>
                    <Typography variant="subtitle1" fontWeight={700} sx={{ mb: 2 }}>Volume Trend (Last 24h)</Typography>
                    <Box sx={{ height: 260 }}>
                      <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={volumeTS}>
                          <defs>
                            <linearGradient id="colorVol" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="5%" stopColor="#2563EB" stopOpacity={0.1}/>
                              <stop offset="95%" stopColor="#2563EB" stopOpacity={0}/>
                            </linearGradient>
                          </defs>
                          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                          <XAxis dataKey="dt" tickFormatter={(v) => format(new Date(v), 'HH:mm')} axisLine={false} tickLine={false} />
                          <YAxis axisLine={false} tickLine={false} />
                          <ChartTooltip contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }} />
                          <Area type="monotone" dataKey="records_added" stroke="#2563EB" strokeWidth={2} fill="url(#colorVol)" />
                        </AreaChart>
                      </ResponsiveContainer>
                    </Box>
                  </Grid>
                  <Grid item xs={12} lg={6}>
                    <Typography variant="subtitle1" fontWeight={700} sx={{ mb: 2 }}>Freshness Delay (Min)</Typography>
                    <Box sx={{ height: 260 }}>
                      <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={[
                          { t: '09:00', v: 5 }, { t: '12:00', v: 12 }, { t: '15:00', v: 45 }, { t: '18:00', v: 8 }, { t: '21:00', v: 10 }
                        ]}>
                          <defs>
                            <linearGradient id="colorDelay" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="5%" stopColor="#EF4444" stopOpacity={0.1}/>
                              <stop offset="95%" stopColor="#EF4444" stopOpacity={0}/>
                            </linearGradient>
                          </defs>
                          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                          <XAxis dataKey="t" axisLine={false} tickLine={false} />
                          <YAxis axisLine={false} tickLine={false} />
                          <ChartTooltip contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }} />
                          <Area type="monotone" dataKey="v" stroke="#EF4444" strokeWidth={2} fill="url(#colorDelay)" />
                        </AreaChart>
                      </ResponsiveContainer>
                    </Box>
                  </Grid>
                </Grid>
              </Box>
            )}

            {activeTab === 1 && (
              <Box>
                 <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                    <Typography variant="subtitle1" fontWeight={700}>Schema Definition</Typography>
                    <Chip label="Match: 100%" color="success" size="small" />
                 </Box>
                 <TableContainer border="1px solid #E2E8F0">
                    <Table size="small">
                       <TableHead sx={{ bgcolor: '#F8FAFC' }}>
                          <TableRow>
                             <TableCell sx={{ fontWeight: 700 }}>Column</TableCell>
                             <TableCell sx={{ fontWeight: 700 }}>Type</TableCell>
                             <TableCell sx={{ fontWeight: 700 }}>Null %</TableCell>
                             <TableCell sx={{ fontWeight: 700 }}>Status</TableCell>
                          </TableRow>
                       </TableHead>
                       <TableBody>
                          {schemaData.map((col, i) => (
                             <TableRow key={i}>
                                <TableCell sx={{ fontWeight: 600 }}>{col.column_name}</TableCell>
                                <TableCell><Chip label={col.data_type} size="small" variant="outlined" sx={{ fontSize: '10px' }} /></TableCell>
                                <TableCell>0.15%</TableCell>
                                <TableCell><Box sx={{ width: 60, height: 6, bgcolor: 'success.main', borderRadius: 1 }} /></TableCell>
                             </TableRow>
                          ))}
                       </TableBody>
                    </Table>
                 </TableContainer>
              </Box>
            )}

            {activeTab === 2 && (
              <Box>
                {incidents.length === 0 ? (
                  <Box sx={{ textAlign: 'center', py: 6 }}>
                    <CheckIcon sx={{ fontSize: 48, color: 'success.main', mb: 2 }} />
                    <Typography>No active incidents for this asset.</Typography>
                  </Box>
                ) : (
                  incidents.map((inc, i) => (
                    <Card key={i} variant="outlined" sx={{ mb: 1, borderLeft: '4px solid', borderLeftColor: inc.severity === 'high' ? 'error.main' : 'warning.main' }}>
                      <CardContent sx={{ py: 1.5 }}>
                        <Typography variant="subtitle2" sx={{ fontWeight: 700 }}>{inc.incident_type}</Typography>
                        <Typography variant="body2" color="text.secondary">{inc.message}</Typography>
                      </CardContent>
                    </Card>
                  ))
                )}
              </Box>
            )}
          </Box>
        </Paper>
      </Box>
    );
  };

  return tableParam ? renderDetailView() : renderListView();
};

export default Observability;