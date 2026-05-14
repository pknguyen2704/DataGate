import React from 'react';
import { Box, Typography, Paper, Stack, Divider, Grid } from "@mui/material";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const AnomalyDetection = ({ detailData }) => {
  // Prepare data for SHAP Chart with guard rails
  const topFeatures = detailData?.top_features || [];
  const shapData = [...topFeatures]
    .sort((a, b) => Math.abs(b.shap_score || 0) - Math.abs(a.shap_score || 0))
    .slice(0, 10);

  const aucScore = detailData?.auc_score ?? 0;
  const aucThreshold = detailData?.auc_threshold ?? 0;

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={4}>
        <Typography variant="caption" color="text.secondary" fontWeight={700}>ANOMALY SCORE</Typography>
        <Paper variant="outlined" sx={{ p: 2, mt: 1, borderRadius: 3, mb: 3, bgcolor: '#f8fafc' }}>
          <Stack direction="row" justifyContent="space-around" spacing={2} divider={<Divider orientation="vertical" flexItem />}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h4" color="primary.main" fontWeight={900}>{aucScore.toFixed(4)}</Typography>
              <Typography variant="caption" fontWeight={600} color="text.secondary">AUC SCORE</Typography>
            </Box>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h4" color="error.main" fontWeight={900}>{aucThreshold.toFixed(4)}</Typography>
              <Typography variant="caption" fontWeight={600} color="text.secondary">THRESHOLD</Typography>
            </Box>
          </Stack>
        </Paper>

        {detailData?.model_config_params && (
          <Box>
            <Typography variant="caption" color="text.secondary" fontWeight={700}>MODEL CONFIGURATION</Typography>
            <Paper variant="outlined" sx={{ p: 2, mt: 1, bgcolor: '#ffffff', borderRadius: 3 }}>
              <Grid container spacing={2}>
                {Object.entries(detailData.model_config_params).map(([k, v]) => (
                  <Grid item xs={6} key={k}>
                    <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase', fontSize: '0.65rem' }}>{k.replace(/_/g, ' ')}</Typography>
                    <Typography variant="body2" fontWeight={700}>{v}</Typography>
                  </Grid>
                ))}
              </Grid>
            </Paper>
          </Box>
        )}
      </Grid>

      <Grid item xs={12} md={8}>
        <Typography variant="caption" color="text.secondary" fontWeight={700}>FEATURE IMPORTANCE (SHAP VALUES)</Typography>
        <Paper variant="outlined" sx={{ mt: 1, p: 2, borderRadius: 3, height: 400 }}>
          {shapData.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                layout="vertical"
                data={shapData}
                margin={{ top: 5, right: 30, left: 100, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={true} stroke="#f1f5f9" />
                <XAxis 
                  type="number" 
                  stroke="#64748b" 
                  fontSize={10} 
                  tickFormatter={(val) => val.toFixed(2)}
                />
                <YAxis 
                  type="category" 
                  dataKey="feature_name" 
                  stroke="#64748b" 
                  fontSize={11} 
                  fontWeight={600}
                  width={120}
                  tick={{ fill: '#475569' }}
                />
                <Tooltip 
                  cursor={{ fill: '#f1f5f9' }}
                  contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)' }}
                />
                <Bar 
                  dataKey="shap_score" 
                  radius={[0, 4, 4, 0]} 
                  barSize={20}
                >
                  {shapData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={(entry.shap_score || 0) > 0 ? '#3b82f6' : '#ef4444'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
              <Typography variant="body2" color="text.secondary">No SHAP features available.</Typography>
            </Box>
          )}
        </Paper>
      </Grid>
    </Grid>
  );
};

export default AnomalyDetection;