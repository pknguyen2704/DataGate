import React, { useState, useEffect } from 'react';
import { 
  Box, Typography, Grid, Paper, Chip, 
  CircularProgress, Card, CardContent, 
  LinearProgress, Stack, Avatar, Table, TableBody, TableCell, TableContainer, TableHead, TableRow
} from '@mui/material';
import { 
  Psychology as ModelIcon,
  AutoGraph as AnomalyIcon,
  Troubleshoot as RootCauseIcon,
  Memory as FeatureIcon,
  Timeline as TimelineIcon,
} from '@mui/icons-material';
import { mlQualityApi } from '../../apis/mlQuality';
import { format } from 'date-fns';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const AnomalyDetection = () => {
  const [runs, setRuns] = useState([]);
  const [selectedRun, setSelectedRun] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    try {
      const res = await mlQualityApi.getRuns();
      setRuns(res.data);
      if (res.data.length > 0) {
        const detail = await mlQualityApi.getRunDetail(res.data[0].id);
        setSelectedRun(detail.data);
      }
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchData(); }, []);

  if (loading && !selectedRun) return <Box sx={{ display: 'flex', justifyContent: 'center', py: 10 }}><CircularProgress /></Box>;

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 800 }}>ML Anomaly Detection</Typography>
        <Typography variant="body1" color="text.secondary">Deep learning based distribution shift and outlier detection.</Typography>
      </Box>

      {selectedRun ? (
        <Grid container spacing={3}>
          {/* Summary Section */}
          <Grid item xs={12} md={4}>
            <Card className="glass-card" sx={{ height: '100%', bgcolor: 'primary.dark', color: 'white', position: 'relative' }}>
              <CardContent sx={{ p: 4 }}>
                <ModelIcon sx={{ fontSize: 40, mb: 2, opacity: 0.8 }} />
                <Typography variant="h6" sx={{ opacity: 0.9 }}>Model Confidence (AUC)</Typography>
                <Typography variant="h1" sx={{ fontWeight: 900, my: 1 }}>{selectedRun.anomaly_score.toFixed(3)}</Typography>
                <Chip 
                  label={selectedRun.status === 'ALERT' ? 'ANOMALY DETECTED' : 'NORMAL'} 
                  color={selectedRun.status === 'ALERT' ? 'error' : 'success'} 
                  sx={{ fontWeight: 800, px: 2 }}
                />
                <Typography variant="body2" sx={{ mt: 3, opacity: 0.7 }}>
                   Training data: Previous 14 days<br/>
                   Inference data: Latest batch ({selectedRun.partition_key})
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* Feature Importance (SHAP) */}
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 3, height: '100%' }}>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <FeatureIcon color="primary" /> Feature Importance (SHAP)
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 4 }}>
                Which columns contributed most to this distribution shift?
              </Typography>
              <Box sx={{ height: 260 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={selectedRun.features} layout="vertical" margin={{ left: 40 }}>
                    <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f1f5f9" />
                    <XAxis type="number" hide />
                    <YAxis dataKey="column_name" type="category" axisLine={false} tickLine={false} tick={{ fontSize: 12, fontWeight: 600 }} />
                    <Tooltip cursor={{ fill: '#F1F5F9' }} />
                    <Bar dataKey="importance_score" radius={[0, 4, 4, 0]}>
                      {selectedRun.features.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={index === 0 ? '#2563EB' : '#94A3B8'} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </Box>
            </Paper>
          </Grid>

          {/* Root Cause Analysis */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <RootCauseIcon color="warning" /> Segmented Root Cause
              </Typography>
              <Stack spacing={2} sx={{ mt: 2 }}>
                {[
                  { segment: 'Region: North America', shift: '+62%', impact: 'High' },
                  { segment: 'App Version: 4.2.1', shift: '-12%', impact: 'Medium' },
                  { segment: 'Device: Android', shift: '+5%', impact: 'Low' },
                ].map((s, i) => (
                  <Box key={i} sx={{ p: 2, bgcolor: '#F8FAFC', borderRadius: '12px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="body2" fontWeight={700}>{s.segment}</Typography>
                    <Box sx={{ textAlign: 'right' }}>
                      <Typography variant="caption" color="error.main" fontWeight={800} display="block">{s.shift} Shift</Typography>
                      <Chip label={s.impact} size="small" sx={{ height: 16, fontSize: '9px' }} />
                    </Box>
                  </Box>
                ))}
              </Stack>
            </Paper>
          </Grid>

          {/* Anomalous Rows */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <AnomalyIcon color="error" /> Anomalous Rows Sample
              </Typography>
              <TableContainer sx={{ mt: 2 }}>
                <Table size="small">
                  <TableHead sx={{ bgcolor: '#F8FAFC' }}>
                    <TableRow>
                      <TableCell sx={{ fontWeight: 700, fontSize: '11px' }}>ID</TableCell>
                      <TableCell sx={{ fontWeight: 700, fontSize: '11px' }}>Reason</TableCell>
                      <TableCell sx={{ fontWeight: 700, fontSize: '11px' }}>Details</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {[1, 2, 3].map(i => (
                      <TableRow key={i}>
                        <TableCell sx={{ fontSize: '11px' }}>ROW_{842+i}</TableCell>
                        <TableCell><Chip label="Outlier" size="small" color="error" variant="outlined" sx={{ height: 18, fontSize: '10px' }} /></TableCell>
                        <TableCell sx={{ fontSize: '11px', color: 'text.secondary' }}>fare_amount &gt; 5.2 std dev</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Paper>
          </Grid>
        </Grid>
      ) : (
        <Paper sx={{ p: 10, textAlign: 'center' }}>
          <Typography color="text.secondary">No ML runs detected. Trigger an ML scan from Observability to see results.</Typography>
        </Paper>
      )}
    </Box>
  );
};

export default AnomalyDetection;