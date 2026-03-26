import React from 'react';
import { Box, Paper, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Card, CardContent, Divider, FormControl, InputLabel, Select, MenuItem } from '@mui/material';
import { TableChart as TableChartIcon, QueryStats as StatsIcon, Insights as InsightsIcon } from '@mui/icons-material';
import ReactECharts from 'echarts-for-react';
import { format } from 'date-fns';

const ProfilingDashboard = ({
  selectedRun, selectedColumn, handleSelectColumn, histogramData, trendData, trendMetric, onMetricChange
}) => {
  if (!selectedRun) return null;

  const getGaugeOption = () => ({
    series: [{
      type: 'gauge', startAngle: 180, endAngle: 0, center: ['50%', '75%'], radius: '90%',
      min: 0, max: 100, splitNumber: 5,
      progress: { show: true, width: 12, itemStyle: { color: '#1a237e' } },
      pointer: { show: false }, axisLine: { lineStyle: { width: 12 } },
      axisTick: { show: false }, splitLine: { show: false }, axisLabel: { show: false },
      detail: { fontSize: 24, offsetCenter: [0, -10], formatter: '{value}%', color: 'inherit' },
      data: [{ value: Math.round((selectedColumn?.completeness || 0) * 100) }]
    }]
  });

  const getHistogramOption = () => ({
    title: { text: `Values: ${selectedColumn?.column_name || ''}`, left: 'center', textStyle: { fontSize: 13 } },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: histogramData.map(d => d.bin_value), axisLabel: { rotate: 25, fontSize: 10 } },
    yAxis: { type: 'value', axisLabel: { fontSize: 10 } },
    grid: { bottom: '20%', left: '15%', right: '5%' },
    series: [{ data: histogramData.map(d => d.absolute_count), type: 'bar', itemStyle: { color: '#1a237e' } }]
  });

  const getTrendOption = () => ({
    title: { text: `Trend: ${trendMetric.toUpperCase()}`, left: 'center', textStyle: { fontSize: 13 } },
    tooltip: { trigger: 'axis' },
    grid: { bottom: '20%', left: '10%', right: '5%' },
    xAxis: { type: 'category', data: trendData.map(d => format(new Date(d.created_at), 'MM/dd HH:mm')) },
    yAxis: { type: 'value' },
    series: [{ data: trendData.map(d => d.value), type: 'line', smooth: true, areaStyle: { opacity: 0.1 }, itemStyle: { color: '#ff9800' } }]
  });

  const getStatsRadarOption = () => (selectedColumn?.mean != null ? {
    title: { text: 'Metrics Radar', left: 'center', textStyle: { fontSize: 13 } },
    radar: {
      indicator: [
        { name: 'Min', max: selectedColumn.maximum || 1 },
        { name: 'Mean', max: selectedColumn.maximum || 1 },
        { name: 'Max', max: selectedColumn.maximum || 1 },
        { name: 'StdDev', max: selectedColumn.maximum || 1 },
      ],
      center: ['50%', '60%'], radius: '65%'
    },
    series: [{
      type: 'radar', areaStyle: { color: 'rgba(26, 35, 126, 0.3)' },
      data: [{ value: [selectedColumn.minimum || 0, selectedColumn.mean || 0, selectedColumn.maximum || 0, selectedColumn.std_dev || 0], name: 'Column Stats' }]
    }]
  } : { title: { text: 'No numeric stats', left: 'center', textStyle: { fontSize: 13 } } });

  return (
    <Box sx={{ display: 'flex', flexDirection: { xs: 'column', lg: 'row' }, gap: 3, pt: 2 }}>
      {/* Left Column */}
      <Box sx={{ flex: { xs: '1', lg: '0 0 35%' }, display: 'flex', flexDirection: 'column', gap: 3 }}>
        <Card sx={{ bgcolor: 'white', borderTop: '4px solid #1a237e', boxShadow: 2 }}>
          <CardContent>
            <Typography variant="h6" display="flex" alignItems="center" gutterBottom color="primary.main">
              <StatsIcon sx={{ mr: 1 }}/> Data Quality Score
            </Typography>
            <Box display="flex" justifyContent="space-between" mb={2}>
              <Box><Typography variant="caption" color="text.secondary">Total Rows</Typography><Typography variant="h5" fontWeight="bold">{selectedRun.num_records.toLocaleString()}</Typography></Box>
              <Box><Typography variant="caption" color="text.secondary" align="right">Table</Typography><Typography variant="h6" align="right" color="text.primary">{selectedRun.table_name}</Typography></Box>
            </Box>
            <Divider sx={{ my: 2 }} />
            <Typography variant="caption" color="text.secondary">Completeness Indicator</Typography>
            <Box sx={{ height: 160, mt: -2 }}>
              <ReactECharts option={getGaugeOption()} style={{ height: '100%', width: '100%' }} />
            </Box>
          </CardContent>
        </Card>

        <TableContainer component={Paper} elevation={2} sx={{ flexGrow: 1, maxHeight: 500 }}>
          <Typography variant="subtitle2" sx={{ p: 2, fontWeight: 'bold', bgcolor: '#f4f6f8' }}>
            <TableChartIcon sx={{ mr: 1, verticalAlign: 'middle', fontSize: 18 }} color="primary"/> Select Column
          </Typography>
          <Table size="small" stickyHeader>
            <TableHead>
              <TableRow>
                <TableCell>Column</TableCell>
                <TableCell align="right">Health</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {selectedRun.columns.map((col) => (
                <TableRow 
                  key={col.id} 
                  hover 
                  selected={selectedColumn?.id === col.id} 
                  onClick={() => handleSelectColumn(col, selectedRun.table_name)} 
                  sx={{ cursor: 'pointer', '&.Mui-selected': { bgcolor: 'rgba(26, 35, 126, 0.08)' } }}
                >
                  <TableCell sx={{ fontWeight: selectedColumn?.id === col.id ? 700 : 400 }}>{col.column_name}</TableCell>
                  <TableCell align="right">
                    <Typography variant="body2" sx={{ color: col.completeness > 0.9 ? 'success.main' : 'error.main', fontWeight: 'bold' }}>
                      {(col.completeness * 100).toFixed(0)}%
                    </Typography>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Box>

      {/* Right Column: Charts */}
      <Box sx={{ flex: '1', display: 'flex', flexDirection: 'column', gap: 3 }}>
        <Box sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' }, gap: 3, flex: 1 }}>
          <Paper elevation={2} sx={{ p: 2, flex: 1, display: 'flex', flexDirection: 'column', minHeight: 300 }}>
            <ReactECharts option={getHistogramOption()} style={{ flex: 1, minHeight: '100%' }} notMerge={true} />
          </Paper>
          <Paper elevation={2} sx={{ p: 2, flex: 1, display: 'flex', flexDirection: 'column', minHeight: 300 }}>
             <ReactECharts option={getStatsRadarOption()} style={{ flex: 1, minHeight: '100%' }} notMerge={true} />
          </Paper>
        </Box>

        <Paper elevation={2} sx={{ p: 3, flex: 1, minHeight: 380 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6" display="flex" alignItems="center" color="text.primary">
              <InsightsIcon sx={{ mr: 1 }} color="warning"/> Trend Analytics
            </Typography>
            <FormControl size="small" sx={{ minWidth: 150 }}>
              <InputLabel>Metric</InputLabel>
              <Select value={trendMetric} label="Metric" onChange={onMetricChange}>
                <MenuItem value="completeness">Completeness</MenuItem>
                <MenuItem value="mean">Mean Value</MenuItem>
                <MenuItem value="maximum">Max Value</MenuItem>
                <MenuItem value="minimum">Min Value</MenuItem>
                <MenuItem value="std_dev">Std Deviation</MenuItem>
              </Select>
            </FormControl>
          </Box>
          <Box sx={{ height: 300 }}>
             <ReactECharts option={getTrendOption()} style={{ height: '100%', width: '100%' }} notMerge={true} />
          </Box>
        </Paper>
      </Box>
    </Box>
  );
};
export default ProfilingDashboard;