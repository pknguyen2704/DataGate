import React from "react";
import {
  Box,
  Grid,
  Paper,
  Typography,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  useTheme,
} from "@mui/material";
import {
  AccessTime as FreshnessIcon,
  BarChart as VolumeIcon,
  Rule as RuleIcon,
  Timeline as AnomalyIcon,
  TrendingUp,
  TrendingDown,
  ChevronRight,
} from "@mui/icons-material";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
} from "recharts";

const mockVolumeData = [
  { time: "00:00", value: 1200 },
  { time: "04:00", value: 1500 },
  { time: "08:00", value: 3200 },
  { time: "12:00", value: 4500 },
  { time: "16:00", value: 4200 },
  { time: "20:00", value: 3800 },
  { time: "23:59", value: 3500 },
];

const mockAnomalyData = [
  { time: "00:00", score: 0.1 },
  { time: "04:00", score: 0.15 },
  { time: "08:00", score: 0.8 },
  { time: "12:00", score: 0.2 },
  { time: "16:00", score: 0.3 },
  { time: "20:00", score: 0.1 },
  { time: "23:59", score: 0.1 },
];

const KPICard = ({ title, value, change, icon, color, status }) => (
  <Paper sx={{ p: 2.5, height: '100%', position: 'relative', overflow: 'hidden' }}>
    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
      <Box sx={{ p: 1, borderRadius: '10px', bgcolor: `${color}15`, color: color }}>
        {icon}
      </Box>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
        {change > 0 ? (
          <TrendingUp sx={{ fontSize: 16, color: 'success.main' }} />
        ) : (
          <TrendingDown sx={{ fontSize: 16, color: 'error.main' }} />
        )}
        <Typography variant="caption" sx={{ fontWeight: 700, color: change > 0 ? 'success.main' : 'error.main' }}>
          {Math.abs(change)}%
        </Typography>
      </Box>
    </Box>
    <Typography variant="h4" sx={{ fontWeight: 800, mb: 0.5 }}>{value}</Typography>
    <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>{title}</Typography>
    {status && (
      <Box sx={{ mt: 1.5, display: 'flex', alignItems: 'center' }}>
        <Box className={`status-dot status-${status}`} />
        <Typography variant="caption" sx={{ textTransform: 'capitalize', fontWeight: 600 }}>
          {status}
        </Typography>
      </Box>
    )}
  </Paper>
);

const PipelineNode = ({ name, status, icon }) => (
  <Box sx={{ textAlign: 'center', position: 'relative' }}>
    <Box 
      sx={{ 
        width: 80, 
        height: 80, 
        borderRadius: '20px', 
        bgcolor: '#FFFFFF', 
        border: '2px solid',
        borderColor: status === 'healthy' ? 'success.main' : status === 'warning' ? 'warning.main' : 'error.main',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        mx: 'auto',
        mb: 1.5,
        boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
        cursor: 'pointer',
        transition: 'transform 0.2s',
        '&:hover': { transform: 'scale(1.05)' }
      }}
    >
      <Typography variant="h6" sx={{ color: 'text.main' }}>{icon}</Typography>
    </Box>
    <Typography variant="subtitle2" sx={{ fontWeight: 700 }}>{name}</Typography>
    <Chip 
      label={status} 
      size="small" 
      color={status === 'healthy' ? 'success' : status === 'warning' ? 'warning' : 'error'}
      sx={{ height: 20, fontSize: '0.65rem', fontWeight: 700, mt: 0.5 }} 
    />
  </Box>
);

const Home = () => {
  const theme = useTheme();

  return (
    <Box sx={{ p: 4, height: '100%', overflow: 'auto' }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight="800" sx={{ mb: 0.5 }}>System Overview</Typography>
        <Typography variant="body1" color="text.secondary">
          Health monitoring and data quality metrics for the last 24 hours.
        </Typography>
      </Box>

      {/* KPI Section */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard 
            title="Data Freshness Status" 
            value="42m ago" 
            change={12} 
            icon={<FreshnessIcon />} 
            color="#2563EB" 
            status="healthy"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard 
            title="Volume Change" 
            value="1.2M logs" 
            change={5.4} 
            icon={<VolumeIcon />} 
            color="#8B5CF6"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard 
            title="Failed Rules" 
            value="14" 
            change={-2} 
            icon={<RuleIcon />} 
            color="#EF4444" 
            status="danger"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard 
            title="ML Anomaly Score" 
            value="0.14" 
            change={8} 
            icon={<AnomalyIcon />} 
            color="#F59E0B" 
            status="warning"
          />
        </Grid>
      </Grid>

      {/* Pipeline Health & Time Series */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={5}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" sx={{ mb: 3 }}>Pipeline Health</Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', px: 2, position: 'relative' }}>
              <Box sx={{ position: 'absolute', top: 40, left: '15%', right: '15%', height: 2, bgcolor: '#E2E8F0', zIndex: 0 }} />
              <PipelineNode name="Bronze" status="healthy" icon="B" />
              <PipelineNode name="Silver" status="warning" icon="S" />
              <PipelineNode name="Gold" status="healthy" icon="G" />
            </Box>
            <Box sx={{ mt: 4, p: 2, bgcolor: '#F8FAFC', borderRadius: '12px' }}>
              <Typography variant="caption" color="text.secondary" display="block" gutterBottom>Latest Alert</Typography>
              <Typography variant="body2" sx={{ fontWeight: 600 }}>
                Silver layer: Schema mismatch detected in "orders_silver" (+2 columns)
              </Typography>
            </Box>
          </Paper>
        </Grid>
        <Grid item xs={12} md={7}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
              <Typography variant="h6">Volume & Anomaly Trends</Typography>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Chip label="24h" size="small" variant="filled" color="primary" />
                <Chip label="7d" size="small" variant="outlined" />
              </Box>
            </Box>
            <Box sx={{ height: 300, minHeight: 300 }}>
              <ResponsiveContainer width="99%" height="100%">
                <AreaChart data={mockVolumeData}>
                  <defs>
                    <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={theme.palette.primary.main} stopOpacity={0.1}/>
                      <stop offset="95%" stopColor={theme.palette.primary.main} stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis dataKey="time" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748B' }} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748B' }} />
                  <Tooltip 
                    contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}
                  />
                  <Area type="monotone" dataKey="value" stroke={theme.palette.primary.main} strokeWidth={2} fillOpacity={1} fill="url(#colorValue)" />
                </AreaChart>
              </ResponsiveContainer>
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* Incidents Table */}
      <Paper sx={{ overflow: 'hidden' }}>
        <Box sx={{ p: 2.5, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">Active Incidents</Typography>
          <Button size="small">View All</Button>
        </Box>
        <TableContainer>
          <Table>
            <TableHead sx={{ bgcolor: '#F8FAFC' }}>
              <TableRow>
                <TableCell sx={{ fontWeight: 700 }}>Dataset</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Issue Type</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Severity</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Status</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Timestamp</TableCell>
                <TableCell sx={{ fontWeight: 700 }} align="right">Action</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {[
                { dataset: 'raw_uber_trips', type: 'Freshness Delay', severity: 'Critical', status: 'Open', time: '12 mins ago' },
                { dataset: 'silver_clean_trips', type: 'ML Anomaly', severity: 'Medium', status: 'Investigating', time: '1 hour ago' },
                { dataset: 'gold_trips_agg', type: 'Rule Violation', severity: 'Low', status: 'Resolved', time: '3 hours ago' },
              ].map((row, i) => (
                <TableRow key={i} hover>
                  <TableCell sx={{ fontWeight: 600 }}>{row.dataset}</TableCell>
                  <TableCell>{row.type}</TableCell>
                  <TableCell>
                    <Chip 
                      label={row.severity} 
                      size="small" 
                      sx={{ 
                        bgcolor: row.severity === 'Critical' ? '#FEE2E2' : row.severity === 'Medium' ? '#FEF3C7' : '#E0F2FE',
                        color: row.severity === 'Critical' ? '#EF4444' : row.severity === 'Medium' ? '#D97706' : '#0284C7',
                        fontWeight: 700,
                        fontSize: '0.7rem'
                      }} 
                    />
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Box className={`status-dot status-${row.status === 'Open' ? 'danger' : row.status === 'Resolved' ? 'healthy' : 'warning'}`} />
                      <Typography variant="body2">{row.status}</Typography>
                    </Box>
                  </TableCell>
                  <TableCell color="text.secondary">{row.time}</TableCell>
                  <TableCell align="right">
                    <Button size="small" variant="outlined">Investigate</Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Box>
  );
};

export default Home;