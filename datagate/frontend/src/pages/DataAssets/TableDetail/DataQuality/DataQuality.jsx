import React, { useState } from "react";
import {
  Box, Typography, Paper, Table, TableBody, TableCell,
  TableHead, TableRow, TableContainer, Button, IconButton,
  Chip, Grid, Stack, TextField, MenuItem, FormControl,
  InputLabel, Select, Tooltip, CircularProgress,
  Tabs, Tab, TablePagination
} from "@mui/material";
import {
  ArrowBack, CheckCircle, Refresh, CheckCircleOutline
} from "@mui/icons-material";
import { useParams } from "react-router-dom";
import { dataQualityApi } from "~/apis/dataQualityApi";
import { dataAssetsApi } from "~/apis/dataAssetsApi";
import { useApiResource } from "~/hooks/useApiResource";
import { useSelector } from "react-redux";
import { format } from "date-fns";
import { Panel, Stat, StateBox, StatusChip } from "~/components/Common/DataDisplay";

import AnomalyDetection from "./AnomalyDetection/AnomalyDetection";
import Profile from "./Profile/Profile";
import Metadata from "./Metadata/Metadata";
import Rule from "./Rule/Rule";

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
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);

  // Permissions
  const isAdmin = user?.roles?.some(r => r === "Admin" || r?.name === "Admin");
  const hasResolvePerm = user?.permissions?.some(p => p === "quality:resolve" || p?.code === "quality:resolve");
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
    ...filters,
    page: page + 1,
    page_size: pageSize
  }), [tableId, currentType, filters, page, pageSize]);

  const handleFilterChange = (name, value) => {
    setFilters(prev => ({ ...prev, [name]: value }));
    setPage(0);
  };

  const handleResolve = async (type, id) => {
    try {
      if (type === "metadata") await dataQualityApi.resolveMetadata(id);
      else if (type === "profiling") await dataQualityApi.resolveProfiling(id);
      else if (type === "rule") await dataQualityApi.resolveRule(id);
      else if (type === "anomaly") await dataQualityApi.resolveAnomaly(id);

      resultsRes.reload();
      summaryRes.reload();
    } catch (error) {
      console.error(error);
      alert("Resolve failed");
    }
  };

  const summary = summaryRes.data || { total_checks: 0, total_pass: 0, total_fail: 0, warning_fail: 0, critical_fail: 0, unresolved_alerts: 0 };

  return (
    <Box sx={{ p: 3 }}>
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
          <Tabs value={activeTab} onChange={(e, v) => { setActiveTab(v); setPage(0); }}>
            <Tab label="Metadata Checks" />
            <Tab label="Profiling Checks" />
            {showRules && <Tab label="Data Rules" />}
            {showAnomaly && <Tab label="Anomaly Results" />}
          </Tabs>
          <Button startIcon={<Refresh />} onClick={() => { summaryRes.reload(); resultsRes.reload(); }}>Refresh</Button>
        </Box>

        {/* Filter Bar */}
        {currentType !== "anomaly" && (
          <Paper variant="outlined" sx={{ p: 2, borderRadius: 2, bgcolor: 'background.default' }}>
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
            <AnomalyTab 
              results={resultsRes.data?.items || []} 
              total={resultsRes.data?.total || 0}
              page={page} setPage={setPage} pageSize={pageSize} setPageSize={setPageSize}
              handleResolve={handleResolve} canResolve={canResolve} 
            />
          ) : (
            <GenericTab 
              type={currentType} 
              results={resultsRes.data?.items || []} 
              total={resultsRes.data?.total || 0}
              page={page} setPage={setPage} pageSize={pageSize} setPageSize={setPageSize}
              handleResolve={handleResolve} canResolve={canResolve} 
            />
          )}
        </StateBox>
      </Stack>
    </Box>
  );
};

const GenericTab = ({ type, results, total, page, pageSize, setPage, setPageSize, handleResolve, canResolve }) => {
  const [selectedId, setSelectedId] = useState(null);
  const [detailData, setDetailData] = useState(null);
  const [loading, setLoading] = useState(false);

  React.useEffect(() => {
    const loadDetail = async (id) => {
      setLoading(true);
      try {
        let res;
        if (type === "metadata") res = await dataQualityApi.getMetadataDetail(id);
        else if (type === "profiling") res = await dataQualityApi.getProfilingDetail(id);
        else if (type === "rule") res = await dataQualityApi.getRuleDetail(id);
        
        setDetailData(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    if (selectedId) {
      loadDetail(selectedId);
    }
  }, [selectedId, type]);

  const DetailComponent = type === "metadata" ? Metadata : type === "profiling" ? Profile : Rule;

  return (
    <Box sx={{ width: '100%' }}>
      <Grid container spacing={selectedId ? 3 : 0}>
        <Grid item xs={selectedId ? 7 : 12}>
          <TableContainer component={Paper} variant="outlined" sx={{ borderRadius: 2, overflow: 'hidden' }}>
            <Table size="small">
              <TableHead>
                <TableRow sx={{ bgcolor: 'primary.main' }}>
                  <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Target</TableCell>
                  <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Metric / Rule</TableCell>
                  <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Status</TableCell>
                  {!selectedId && <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Severity</TableCell>}
                  {!selectedId && <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Value</TableCell>}
                  <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Execution Date</TableCell>
                  {!selectedId && <TableCell align="center" sx={{ color: 'white', fontWeight: 'bold' }}>Actions</TableCell>}
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
                      <Typography variant="body2" fontWeight={600}>{r.column_name || 'Table'}</Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">{r.metric_name || r.message || '-'}</Typography>
                    </TableCell>
                    <TableCell>
                      <StatusChip value={r.status} />
                    </TableCell>
                    {!selectedId && (
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
                    )}
                    {!selectedId && (
                      <TableCell>
                        <Typography variant="body2">
                          {r.actual_value !== null && r.actual_value !== undefined ? Number(r.actual_value).toFixed(4) : '-'}
                          {r.threshold_value !== null && r.threshold_value !== undefined && (
                            <Typography variant="caption" color="text.secondary" sx={{ ml: 1 }}>
                              ({Number(r.threshold_value).toFixed(4)})
                            </Typography>
                          )}
                        </Typography>
                      </TableCell>
                    )}
                    <TableCell>
                      <Typography variant="caption" color="text.secondary">
                        {format(new Date(r.processing_date_hour), "yyyy-MM-dd HH:mm")}
                      </Typography>
                    </TableCell>
                    {!selectedId && (
                      <TableCell align="center">
                        <Stack direction="row" spacing={1} justifyContent="center" onClick={(e) => e.stopPropagation()}>
                          {r.status?.toLowerCase() === 'fail' && !r.is_resolved && canResolve && (
                            <Tooltip title="Mark as Resolved">
                              <IconButton size="small" color="error" onClick={() => handleResolve(type, r.id)}>
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
            <TablePagination
              rowsPerPageOptions={[5, 10, 25]}
              component="div"
              count={total}
              rowsPerPage={pageSize}
              page={page}
              onPageChange={(e, newPage) => setPage(newPage)}
              onRowsPerPageChange={(e) => {
                setPageSize(parseInt(e.target.value, 10));
                setPage(0);
              }}
            />
          </TableContainer>
      </Grid>

      {selectedId && (
        <Grid item xs={5}>
          <Box sx={{ position: 'sticky', top: 20 }}>
            {loading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', py: 10 }}><CircularProgress /></Box>
            ) : detailData ? (
              <Box>
                <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="h6" fontWeight={800}>Analysis: {format(new Date(detailData.processing_date_hour), "yyyy-MM-dd HH:mm")}</Typography>
                  <Tooltip title="Back to results">
                    <IconButton onClick={() => setSelectedId(null)} size="small">
                      <ArrowBack fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </Box>
                <DetailComponent detailData={detailData} />
              </Box>
            ) : null}
          </Box>
        </Grid>
      )}
    </Grid>
    </Box>
  );
};

const AnomalyTab = ({ results, total, page, pageSize, setPage, setPageSize, handleResolve, canResolve }) => {
  const [selectedId, setSelectedId] = useState(null);
  const [detailData, setDetailData] = useState(null);
  const [loading, setLoading] = useState(false);

  React.useEffect(() => {
    const loadDetail = async (id) => {
      setLoading(true);
      try {
        const res = await dataQualityApi.getAnomalyDetail(id);
        setDetailData(res.data);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    };

    if (selectedId) {
      loadDetail(selectedId);
    }
  }, [selectedId]);

  return (
    <Box sx={{ width: '100%' }}>
      <Grid container spacing={selectedId ? 3 : 0}>
        <Grid item xs={selectedId ? 4 : 12}>
          <TableContainer component={Paper} variant="outlined" sx={{ borderRadius: 2, overflow: 'hidden' }}>
            <Table size="small">
              <TableHead>
                <TableRow sx={{ bgcolor: 'primary.main' }}>
                  <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Date</TableCell>
                  <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Status</TableCell>
                  <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>AUC</TableCell>
                  {!selectedId && <TableCell align="center" sx={{ color: 'white', fontWeight: 'bold' }}>Actions</TableCell>}
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
                    <TableCell><Typography variant="body2" fontWeight={700}>{r.actual_value !== null ? Number(r.actual_value).toFixed(4) : "N/A"}</Typography></TableCell>
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
            <TablePagination
              rowsPerPageOptions={[5, 10, 25]}
              component="div"
              count={total}
              rowsPerPage={pageSize}
              page={page}
              onPageChange={(e, newPage) => setPage(newPage)}
              onRowsPerPageChange={(e) => {
                setPageSize(parseInt(e.target.value, 10));
                setPage(0);
              }}
            />
          </TableContainer>
      </Grid>

      {selectedId && (
        <Grid item xs={8} sx={{ pr: { xs: 0, md: 2 } }}>
          <Box sx={{ position: 'sticky', top: 20 }}>
            {loading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', py: 10 }}><CircularProgress /></Box>
            ) : detailData ? (
              <Box>
                <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="h6" fontWeight={800}>Analysis: {format(new Date(detailData.processing_date_hour), "yyyy-MM-dd HH:mm")}</Typography>
                  <Tooltip title="Back to anomaly results">
                    <IconButton onClick={() => setSelectedId(null)} size="small">
                      <ArrowBack fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </Box>
                <AnomalyDetection detailData={detailData} />
              </Box>
            ) : null}
          </Box>
        </Grid>
      )}
    </Grid>
    </Box>
  );
};

export default DataQuality;
