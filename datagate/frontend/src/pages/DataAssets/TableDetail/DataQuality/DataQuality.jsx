import React, { useState } from "react";
import {
  Box, Typography, Paper, Table, TableBody, TableCell,
  TableHead, TableRow, TableContainer, Button, IconButton,
  Chip, Grid, Stack, TextField, MenuItem, FormControl,
  InputLabel, Select, Divider, Tooltip, Alert, CircularProgress,
  Tabs, Tab
} from "@mui/material";
import {
  CheckCircle, Refresh, Visibility, CheckCircleOutline
} from "@mui/icons-material";
import { useParams } from "react-router-dom";
import { dataQualityApi } from "~/apis/dataQualityApi";
import { dataAssetsApi } from "~/apis/dataAssetsApi";
import { useApiResource } from "~/hooks/useApiResource";
import { useSelector } from "react-redux";
import { format } from "date-fns";
import { 
  Panel, Stat, StateBox, StatusChip 
} from "~/components/DataGate/Page";

import AnomalyDetection from "./AnomalyDetection/AnomalyDetection";

const DataQuality = () => {
  const { tableId } = useParams();
  const { user } = useSelector(state => state.auth);
  const [activeTab, setActiveTab] = useState(0);

  // Filters
  const [filters, setFilters] = useState({
    processing_date_hour: "",
    status: "",
    severity_level: ""
  });

  // Permissions
  const isAdmin = user?.roles?.some(r => r === "Admin" || r?.name === "Admin");
  const hasResolvePerm = user?.permissions?.some(p => p === "quality:run" || p?.code === "quality:run");
  const canResolve = isAdmin || hasResolvePerm;

  // API Resources
  const tableRes = useApiResource(() => dataAssetsApi.get(tableId), [tableId]);
  const summaryRes = useApiResource(() => dataQualityApi.getSummary({ table_id: tableId }), [tableId]);
  
  const schema = tableRes.data?.schema_name?.toLowerCase();
  const showRules = schema === "gold" || schema === "silver";
  const showAnomaly = schema === "silver";

  const tabTypes = [
    "metadata", 
    "profiling", 
    ...(showRules ? ["rule"] : []),
    ...(showAnomaly ? ["anomaly"] : [])
  ];
  const currentType = tabTypes[activeTab] || tabTypes[0];

  const resultsRes = useApiResource(() => dataQualityApi.listResults({ 
    table_id: tableId, 
    result_type: currentType,
    ...filters 
  }), [tableId, currentType, filters]);

  const handleFilterChange = (name, value) => {
    setFilters(prev => ({ ...prev, [name]: value }));
  };

  const handleResolve = async (type, id) => {
    try {
      if (type === "metadata") await dataQualityApi.resolveMetadata(id);
      else if (type === "profiling") await dataQualityApi.resolveProfiling(id);
      else if (type === "rule") await dataQualityApi.resolveRule(id);
      else if (type === "anomaly") await dataQualityApi.resolveAnomaly(id);

      resultsRes.reload();
      summaryRes.reload();
    } catch (err) {
      alert("Resolve failed");
    }
  };

  const summary = summaryRes.data || { total_checks: 0, total_pass: 0, total_fail: 0, warning_fail: 0, critical_fail: 0, unresolved_alerts: 0 };

  return (
    <Box sx={{ p: { xs: 2, md: 3 }, bgcolor: "background.default", flexGrow: 1, overflow: "auto", display: 'flex', flexDirection: 'column', minWidth: 0 }}>
      <Stack spacing={3} sx={{ width: '100%' }}>
        
        {/* Statistics Section */}
        <Box sx={{ 
          display: 'grid', 
          gridTemplateColumns: { xs: '1fr', sm: 'repeat(3, 1fr)', md: 'repeat(6, 1fr)' }, 
          gap: 2,
          width: '100%'
        }}>
          <Stat label="Total Checks" value={summary.total_checks} tone="blue" />
          <Stat label="Total Pass" value={summary.total_pass} tone="green" />
          <Stat label="Total Fail" value={summary.total_fail} tone="red" />
          <Stat label="Warning Fail" value={summary.warning_fail} tone="amber" />
          <Stat label="Critical Fail" value={summary.critical_fail} tone="red" />
          <Stat label="Unresolved Alerts" value={summary.unresolved_alerts} tone="amber" />
        </Box>

        {/* Tab Selection */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Tabs value={activeTab} onChange={(e, v) => setActiveTab(v)}>
            <Tab label="Metadata Checks" />
            <Tab label="Profiling Checks" />
            {showRules && <Tab label="Data Rules" />}
            {showAnomaly && <Tab label="Anomaly Results" />}
          </Tabs>
          <Button startIcon={<Refresh />} onClick={() => { summaryRes.reload(); resultsRes.reload(); }}>Refresh</Button>
        </Box>

        {/* Filter Bar */}
        {currentType !== "anomaly" && (
          <Paper variant="outlined" sx={{ p: 2, borderRadius: 2, bgcolor: 'white' }}>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth size="small" type="datetime-local" label="Processing Date" InputLabelProps={{ shrink: true }}
                  inputProps={{ step: 1 }}
                  value={filters.processing_date_hour} onChange={(e) => handleFilterChange("processing_date_hour", e.target.value)}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <FormControl fullWidth size="small">
                  <InputLabel>Status</InputLabel>
                  <Select value={filters.status} label="Status" onChange={(e) => handleFilterChange("status", e.target.value)}>
                    <MenuItem value="">All Status</MenuItem>
                    <MenuItem value="pass">Pass</MenuItem>
                    <MenuItem value="fail">Fail</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={4}>
                <FormControl fullWidth size="small">
                  <InputLabel>Severity</InputLabel>
                  <Select value={filters.severity_level} label="Severity" onChange={(e) => handleFilterChange("severity_level", e.target.value)}>
                    <MenuItem value="">All Severity</MenuItem>
                    <MenuItem value="warning">Warning</MenuItem>
                    <MenuItem value="critical">Critical</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          </Paper>
        )}

        {/* Results Content */}
        <StateBox loading={resultsRes.loading} error={resultsRes.error} empty={!(resultsRes.data?.items || []).length}>
          {currentType === "anomaly" ? (
            <AnomalyTab results={resultsRes.data?.items || []} handleResolve={handleResolve} canResolve={canResolve} />
          ) : (
            <Panel title={`${currentType.toUpperCase()} Verification Results`} subtitle={`History of quality checks for ${currentType}.`}>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell sx={{ fontWeight: 'bold' }}>Target</TableCell>
                      <TableCell sx={{ fontWeight: 'bold' }}>Metric / Rule</TableCell>
                      <TableCell sx={{ fontWeight: 'bold' }}>Status</TableCell>
                      <TableCell sx={{ fontWeight: 'bold' }}>Severity</TableCell>
                      <TableCell sx={{ fontWeight: 'bold' }}>Value / Result</TableCell>
                      <TableCell sx={{ fontWeight: 'bold' }}>Execution Date</TableCell>
                      <TableCell align="center" sx={{ fontWeight: 'bold' }}>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {(resultsRes.data?.items || []).map((r) => (
                      <TableRow key={r.id} hover>
                        <TableCell>
                          <Typography variant="body2" fontWeight={600}>{r.column_name || 'Table'}</Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">{r.metric_name || r.message || '-'}</Typography>
                        </TableCell>
                        <TableCell>
                          <StatusChip value={r.status} />
                        </TableCell>
                        <TableCell>
                          {r.severity_level && (
                            <Chip 
                              label={r.severity_level} 
                              size="small" 
                              variant="outlined" 
                              color={r.severity_level === 'critical' ? 'error' : 'warning'} 
                              sx={{ height: 20, fontSize: '0.65rem', textTransform: 'capitalize' }} 
                            />
                          )}
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {r.actual_value !== null ? r.actual_value.toFixed(4) : '-'}
                            {r.threshold_value !== null && (
                              <Typography variant="caption" color="text.secondary" sx={{ ml: 1 }}>
                                ({r.threshold_value.toFixed(4)})
                              </Typography>
                            )}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="caption" color="text.secondary">
                            {format(new Date(r.processing_date_hour), "yyyy-MM-dd HH:mm")}
                          </Typography>
                        </TableCell>
                         <TableCell align="center">
                           <Stack direction="row" spacing={1} justifyContent="center" onClick={(e) => e.stopPropagation()}>
                             {r.status?.toLowerCase() === 'fail' && !r.is_resolved && canResolve && (
                               <Tooltip title="Mark as Resolved">
                                <IconButton size="small" color="error" onClick={() => handleResolve(r.result_type, r.id)}>
                                  <CheckCircleOutline fontSize="small" />
                                </IconButton>
                              </Tooltip>
                            )}
                            {r.is_resolved && <CheckCircle color="success" fontSize="small" />}
                          </Stack>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Panel>
          )}
        </StateBox>
      </Stack>
    </Box>
  );
};

const AnomalyTab = ({ results, handleResolve, canResolve }) => {
  const [selectedId, setSelectedId] = useState(null);
  const [detailData, setDetailData] = useState(null);
  const [loading, setLoading] = useState(false);

  React.useEffect(() => {
    if (selectedId) {
      loadDetail(selectedId);
    }
  }, [selectedId]);

  const loadDetail = async (id) => {
    setLoading(true);
    try {
      const res = await dataQualityApi.getAnomalyDetail(id);
      setDetailData(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Grid container spacing={3}>
      <Grid item xs={selectedId ? 4 : 12}>
        <Panel title="Anomaly Verification History" subtitle="List of recent executions.">
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell sx={{ fontWeight: 'bold' }}>Date</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Status</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>AUC</TableCell>
                  {!selectedId && <TableCell align="center" sx={{ fontWeight: 'bold' }}>Actions</TableCell>}
                </TableRow>
              </TableHead>
              <TableBody>
                {results.map((r) => (
                  <TableRow 
                    key={r.id} 
                    hover 
                    onClick={() => setSelectedId(r.id)} 
                    selected={selectedId === r.id}
                    sx={{ cursor: 'pointer' }}
                  >
                    <TableCell>
                      <Typography variant="body2" color="text.secondary">
                        {format(new Date(r.processing_date_hour), "yyyy-MM-dd HH:mm")}
                      </Typography>
                    </TableCell>
                    <TableCell><StatusChip value={r.status} /></TableCell>
                    <TableCell><Typography variant="body2" fontWeight={700}>{r.actual_value !== null ? r.actual_value.toFixed(4) : "N/A"}</Typography></TableCell>
                    {!selectedId && (
                      <TableCell align="center">
                        <Stack direction="row" spacing={1} justifyContent="center" onClick={(e) => e.stopPropagation()}>
                          {(r.status?.toLowerCase().includes('fail') || r.status?.toLowerCase().includes('failure')) && !r.is_resolved && canResolve && (
                            <Tooltip title="Mark as Resolved">
                              <IconButton size="small" color="error" onClick={() => handleResolve("anomaly", r.id)}>
                                <CheckCircleOutline fontSize="small" />
                              </IconButton>
                            </Tooltip>
                          )}
                          {r.is_resolved && <CheckCircle color="success" fontSize="small" />}
                        </Stack>
                      </TableCell>
                    )}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Panel>
      </Grid>

      {selectedId && (
        <Grid item xs={8}>
          <Box sx={{ position: 'sticky', top: 20 }}>
            {loading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', py: 10 }}><CircularProgress /></Box>
            ) : detailData ? (
              <Box>
                <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="h6" fontWeight={800}>Analysis: {format(new Date(detailData.processing_date_hour), "yyyy-MM-dd HH:mm")}</Typography>
                  <IconButton onClick={() => setSelectedId(null)} size="small"><Visibility /></IconButton>
                </Box>
                <AnomalyDetection detailData={detailData} />
              </Box>
            ) : null}
          </Box>
        </Grid>
      )}
    </Grid>
  );
};

export default DataQuality;