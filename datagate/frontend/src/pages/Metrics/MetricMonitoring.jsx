import React from "react";
import {
  Box,
  Typography,
  Grid,
  Paper,
  Chip,
  Stack,
  useTheme,
} from "@mui/material";
import {
  AssessmentOutlined as MetricsIcon,
  Timeline as TimelineIcon,
  CompareArrows as CompareIcon,
} from "@mui/icons-material";
import {
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const mockMetricData = [
  { time: "09:00", actual: 42, min: 38, max: 46 },
  { time: "10:00", actual: 45, min: 40, max: 50 },
  { time: "11:00", actual: 62, min: 42, max: 52 }, // Anomaly
  { time: "12:00", actual: 48, min: 43, max: 53 },
  { time: "13:00", actual: 50, min: 44, max: 54 },
  { time: "14:00", actual: 52, min: 45, max: 55 },
  { time: "15:00", actual: 51, min: 45, max: 55 },
];

const MetricCard = ({ title, value, unit, status }) => (
  <Paper sx={{ p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
    <Box>
      <Typography variant="caption" color="text.secondary" fontWeight={700}>{title}</Typography>
      <Typography variant="h5" fontWeight={800}>{value} <Typography variant="caption" sx={{ fontWeight: 500 }}>{unit}</Typography></Typography>
    </Box>
    <Chip 
      label={status} 
      size="small" 
      color={status === 'Healthy' ? 'success' : 'error'} 
      sx={{ fontWeight: 800, height: 20, fontSize: '0.65rem' }} 
    />
  </Paper>
);

const MetricMonitoring = () => {
  const theme = useTheme();

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 800 }}>Metric Monitoring</Typography>
        <Typography variant="body1" color="text.secondary">Deep-dive into statistical distributions and time-series profiling.</Typography>
      </Box>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={4}><MetricCard title="Null Rate" value="0.12" unit="%" status="Healthy" /></Grid>
        <Grid item xs={12} md={4}><MetricCard title="Mean Value" value="482.4" unit="USD" status="Healthy" /></Grid>
        <Grid item xs={12} md={4}><MetricCard title="Std Deviation" value="12.5" unit="" status="Healthy" /></Grid>
      </Grid>

      <Paper sx={{ p: 3, mb: 4 }}>
         <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
            <Box>
               <Typography variant="h6">Metric Trend with Confidence Intervals</Typography>
               <Typography variant="caption" color="text.secondary">Actual values vs 95% confidence band (history-based)</Typography>
            </Box>
            <Stack direction="row" spacing={1}>
               <Chip label="Actual" icon={<Box sx={{ width: 8, height: 8, bgcolor: 'primary.main', borderRadius: '50%' }} />} size="small" variant="outlined" />
               <Chip label="Confidence Interval" icon={<Box sx={{ width: 8, height: 8, bgcolor: 'primary.main', opacity: 0.2, borderRadius: '50%' }} />} size="small" variant="outlined" />
            </Stack>
         </Box>
         
         <Box sx={{ height: 400 }}>
            <ResponsiveContainer width="100%" height="100%">
               <ComposedChart data={mockMetricData}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis dataKey="time" axisLine={false} tickLine={false} />
                  <YAxis axisLine={false} tickLine={false} />
                  <Tooltip 
                    contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}
                  />
                  {/* Confidence Interval Band */}
                  <Area 
                    type="monotone" 
                    dataKey="max" 
                    stroke="none" 
                    fill={theme.palette.primary.main} 
                    fillOpacity={0.1} 
                  />
                  <Area 
                    type="monotone" 
                    dataKey="min" 
                    stroke="none" 
                    fill="#FFFFFF" 
                    fillOpacity={1} 
                  />
                  {/* Actual Line */}
                  <Line 
                    type="monotone" 
                    dataKey="actual" 
                    stroke={theme.palette.primary.main} 
                    strokeWidth={3} 
                    dot={(props) => {
                      const { cx, cy, payload } = props;
                      if (payload.actual > payload.max || payload.actual < payload.min) {
                        return <circle cx={cx} cy={cy} r={6} fill={theme.palette.error.main} stroke="none" />;
                      }
                      return <circle cx={cx} cy={cy} r={4} fill={theme.palette.primary.main} stroke="none" />;
                    }}
                  />
               </ComposedChart>
            </ResponsiveContainer>
         </Box>
      </Paper>

      <Typography variant="h6" gutterBottom>Statistical Breakdown</Typography>
      <Grid container spacing={2}>
         {['Completeness', 'Uniqueness', 'Validity', 'Consistency'].map(stat => (
            <Grid item xs={12} sm={6} md={3} key={stat}>
               <Paper sx={{ p: 2, border: '1px solid #E2E8F0', boxShadow: 'none' }}>
                  <Typography variant="caption" fontWeight={700}>{stat}</Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mt: 1 }}>
                     <Typography variant="h5" fontWeight={800}>99.9%</Typography>
                     <Box sx={{ flex: 1, height: 4, bgcolor: '#F1F5F9', borderRadius: 2 }}>
                        <Box sx={{ width: '99.9%', height: '100%', bgcolor: 'success.main', borderRadius: 2 }} />
                     </Box>
                  </Box>
               </Paper>
            </Grid>
         ))}
      </Grid>
    </Box>
  );
};

export default MetricMonitoring;
