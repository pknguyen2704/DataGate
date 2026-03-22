import React, { useState, useEffect } from 'react';
import {
  Box, Paper, Typography, Tab, Tabs,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Card, CardContent, CircularProgress, Chip, IconButton, Alert, 
  Select, MenuItem, FormControl, InputLabel, Divider
} from '@mui/material';
import {
  History as HistoryIcon,
  TableChart as TableChartIcon,
  Refresh as RefreshIcon,
  QueryStats as StatsIcon,
  Insights as InsightsIcon
} from '@mui/icons-material';
import ReactECharts from 'echarts-for-react';
import { format } from 'date-fns';
import { profilingApi } from '../../apis/profiling';

const Profiling = () => {
  const [runs, setRuns] = useState([]);
  const [selectedRun, setSelectedRun] = useState(null);
  const [selectedColumn, setSelectedColumn] = useState(null);
  const [histogramData, setHistogramData] = useState([]);
  const [trendData, setTrendData] = useState([]);
  const [trendMetric, setTrendMetric] = useState('completeness');
  const [loading, setLoading] = useState(false);
  const [runLoading, setRunLoading] = useState(false);
  const [error, setError] = useState(null);
  const [tabValue, setTabValue] = useState(0);

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

  const handleSelectRun = async (runId) => {
    setRunLoading(true);
    try {
      const response = await profilingApi.getRunDetail(runId);
      setSelectedRun(response.data);
      if (response.data.columns.length > 0) {
        handleSelectColumn(response.data.columns[0], response.data.table_name);
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

  // --- Chart Options ---

  const getGaugeOption = () => ({
    series: [{
      type: 'gauge',
      startAngle: 180, endAngle: 0,
      center: ['50%', '75%'], radius: '90%',
      min: 0, max: 100,
      splitNumber: 5,
      progress: { show: true, width: 12, itemStyle: { color: '#1a237e' } },
      pointer: { show: false },
      axisLine: { lineStyle: { width: 12 } },
      axisTick: { show: false },
      splitLine: { show: false },
      axisLabel: { show: false },
      detail: { fontSize: 24, offsetCenter: [0, -10], valueAnimation: true, formatter: '{value}%', color: 'inherit' },
      data: [{ value: Math.round((selectedColumn?.completeness || 0) * 100) }]
    }]
  });

  const getHistogramOption = () => ({
    title: { text: `Values: ${selectedColumn?.column_name}`, left: 'center', textStyle: { fontSize: 13 } },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: histogramData.map(d => d.bin_value), axisLabel: { rotate: 25 } },
    yAxis: { type: 'value' },
    grid: { bottom: '20%', left: '15%' },
    series: [{ 
      data: histogramData.map(d => d.absolute_count), 
      type: 'bar', 
      itemStyle: { color: '#1a237e' } 
    }]
  });

  const getTrendOption = () => ({
    title: { text: `Trend: ${trendMetric.toUpperCase()}`, left: 'center', textStyle: { fontSize: 13 } },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: trendData.map(d => format(new Date(d.created_at), 'MM/dd HH:mm')) },
    yAxis: { type: 'value' },
    series: [{ 
      data: trendData.map(d => d.value), 
      type: 'line', smooth: true, areaStyle: { opacity: 0.1 }, 
      itemStyle: { color: '#ff9800' } 
    }]
  });

  const getStatsRadarOption = () => (selectedColumn?.mean ? {
    title: { text: 'Key Stats Comparison', left: 'center', textStyle: { fontSize: 13 } },
    radar: {
      indicator: [
        { name: 'Min', max: selectedColumn.max || 1 },
        { name: 'Mean', max: selectedColumn.max || 1 },
        { name: 'Max', max: selectedColumn.max || 1 },
        { name: 'StdDev', max: selectedColumn.max || 1 },
      ],
      center: ['50%', '60%'], radius: '65%'
    },
    series: [{
      type: 'radar',
      areaStyle: { color: 'rgba(26, 35, 126, 0.3)' },
      data: [{ value: [selectedColumn.min, selectedColumn.mean, selectedColumn.max, selectedColumn.std_dev], name: 'Column Stats' }]
    }]
  } : { title: { text: 'No numeric stats available', left: 'center' } });

  return (
    <Box sx={{ p: 0 }}>
      {/* Header Section */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Box>
          <Typography variant="h4" fontWeight={800} color="primary.main">Data Observability</Typography>
          <Typography color="text.secondary">Deep analytics into your data quality and distribution</Typography>
        </Box>
        <IconButton onClick={fetchRuns} sx={{ bgcolor: 'white', border: '1px solid #e0e0e0' }}><RefreshIcon /></IconButton>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}

      {/* History Tabs */}
      <Paper sx={{ mb: 4 }}>
        {loading ? <CircularProgress size={20} sx={{ m: 4 }} /> : (
          <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)} variant="scrollable" sx={{ px: 2 }}>
            {runs.map((run) => (
              <Tab key={run.id} label={<Box sx={{ py: 1, textAlign: 'left' }}>
                <Typography variant="body2" fontWeight="bold">{run.table_name}</Typography>
                <Typography variant="caption" color="text.secondary">{format(new Date(run.created_at), 'MM/dd HH:mm')}</Typography>
              </Box>} onClick={() => handleSelectRun(run.id)} />
            ))}
          </Tabs>
        )}
      </Paper>

      {/* Content Section using Flexbox */}
      {runLoading ? <Box display="flex" justifyContent="center" py={10}><CircularProgress /></Box> : selectedRun ? (
        <Box sx={{ display: 'flex', flexDirection: { xs: 'column', lg: 'row' }, gap: 3 }}>
          
          {/* Left Column: Summary & Table */}
          <Box sx={{ flex: { xs: '1', lg: '0 0 30%' }, display: 'flex', flexDirection: 'column', gap: 3 }}>
            <Card sx={{ bgcolor: 'primary.main', color: 'white' }}>
              <CardContent>
                <Typography variant="h6" display="flex" alignItems="center" gutterBottom><StatsIcon sx={{ mr: 1 }}/> Summary</Typography>
                <Box display="flex" justifyContent="space-between" mb={2}>
                  <Box><Typography variant="caption">Total Rows</Typography><Typography variant="h5">{selectedRun.num_records.toLocaleString()}</Typography></Box>
                  <Box><Typography variant="caption" align="right">Table</Typography><Typography variant="h6" align="right">{selectedRun.table_name}</Typography></Box>
                </Box>
                <Divider sx={{ bgcolor: 'rgba(255,255,255,0.2)', my: 2 }} />
                <Typography variant="caption">Data Health Indicator</Typography>
                <Box sx={{ height: 160, mt: -2 }}>
                  <ReactECharts option={getGaugeOption()} style={{ height: '100%', width: '100%' }} />
                </Box>
              </CardContent>
            </Card>

            <TableContainer component={Paper}>
              <Typography variant="subtitle2" sx={{ p: 2, fontWeight: 'bold' }}><TableChartIcon sx={{ mr: 1, verticalAlign: 'middle' }}/> Column Metrics</Typography>
              <Table size="small" stickyHeader>
                <TableHead><TableRow><TableCell>Column</TableCell><TableCell align="right">Comp%</TableCell></TableRow></TableHead>
                <TableBody>
                  {selectedRun.columns.map((col) => (
                    <TableRow key={col.id} hover selected={selectedColumn?.id === col.id} onClick={() => handleSelectColumn(col, selectedRun.table_name)} sx={{ cursor: 'pointer' }}>
                      <TableCell sx={{ fontWeight: 600 }}>{col.column_name}</TableCell>
                      <TableCell align="right">{(col.completeness * 100).toFixed(0)}%</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>

          {/* Right Column: Multiple Charts */}
          <Box sx={{ flex: '1', display: 'flex', flexDirection: 'column', gap: 3 }}>
            <Box sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' }, gap: 3 }}>
              <Paper sx={{ p: 3, flex: 1, height: 400 }}>
                <ReactECharts option={getHistogramOption()} style={{ height: '350px', width: '100%' }} notMerge={true} />
              </Paper>
              <Paper sx={{ p: 3, flex: 1, height: 400 }}>
                <ReactECharts option={getStatsRadarOption()} style={{ height: '350px', width: '100%' }} notMerge={true} />
              </Paper>
            </Box>

            <Paper sx={{ p: 3 }}>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6" display="flex" alignItems="center"><InsightsIcon sx={{ mr: 1 }}/> Trend Analytics</Typography>
                <FormControl size="small" sx={{ minWidth: 150 }}>
                  <InputLabel>Select Metric</InputLabel>
                  <Select value={trendMetric} label="Select Metric" onChange={onMetricChange}>
                    <MenuItem value="completeness">Completeness</MenuItem>
                    <MenuItem value="mean">Mean Value</MenuItem>
                    <MenuItem value="min">Min Value</MenuItem>
                    <MenuItem value="max">Max Value</MenuItem>
                    <MenuItem value="std_dev">Std Deviation</MenuItem>
                  </Select>
                </FormControl>
              </Box>
              <Box sx={{ height: 400 }}>
                <ReactECharts option={getTrendOption()} style={{ height: '100%', width: '100%' }} notMerge={true} />
              </Box>
            </Paper>
          </Box>

        </Box>
      ) : null}
    </Box>
  );
};

export default Profiling;