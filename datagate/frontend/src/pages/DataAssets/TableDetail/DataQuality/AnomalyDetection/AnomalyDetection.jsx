import React from 'react';
import { Box, Typography, Paper, Stack, Divider, Grid } from "@mui/material";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const formatConfigValue = (value) => {
  if (typeof value === 'number' && Number.isFinite(value)) {
    return Number.isInteger(value) ? value.toString() : Number(value.toPrecision(8)).toString();
  }

  const numericValue = Number(value);
  if (typeof value === 'string' && value.trim() !== '' && Number.isFinite(numericValue) && value.length > 10) {
    return Number.isInteger(numericValue) ? numericValue.toString() : Number(numericValue.toPrecision(8)).toString();
  }

  return String(value ?? '-');
};

const AnomalyDetection = ({ detailData }) => {
  // Prepare all SHAP rows with guard rails
  const shapFeatures = detailData?.top_features || [];
  const shapData = [...shapFeatures]
    .sort((a, b) => {
      const rankA = Number.isFinite(a.shap_rank) ? a.shap_rank : Number.MAX_SAFE_INTEGER;
      const rankB = Number.isFinite(b.shap_rank) ? b.shap_rank : Number.MAX_SAFE_INTEGER;

      if (rankA !== rankB) {
        return rankA - rankB;
      }

      return Math.abs(b.shap_score || 0) - Math.abs(a.shap_score || 0);
    });
  const shapChartHeight = Math.max(400, shapData.length * 34 + 80);

  const formatMetricValue = (value) => (
    value !== null && value !== undefined && Number.isFinite(Number(value))
      ? Number(value).toFixed(4)
      : ''
  );
  const aucScore = formatMetricValue(detailData?.auc_score);
  const aucThreshold = formatMetricValue(detailData?.auc_threshold);
  const metricValueSx = {
    fontSize: "1.75rem",
    lineHeight: 1.2,
    maxWidth: "100%",
    overflowWrap: "anywhere",
    wordBreak: "break-word",
    letterSpacing: 0,
  };

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={4}>
        <Typography variant="caption" color="text.secondary" fontWeight={700}>ANOMALY SCORE</Typography>
        <Paper variant="outlined" sx={{ p: 2, mt: 1, borderRadius: 3, mb: 3, bgcolor: '#f8fafc' }}>
          <Stack
            direction={{ xs: "column", sm: "row" }}
            justifyContent="space-around"
            spacing={2}
            divider={<Divider orientation="vertical" flexItem sx={{ display: { xs: "none", sm: "block" } }} />}
            sx={{ minWidth: 0 }}
          >
            <Box sx={{ textAlign: 'center', flex: 1, minWidth: 0 }}>
              <Typography variant="h4" color="primary.main" fontWeight={900} sx={metricValueSx}>
                {aucScore}
              </Typography>
              <Typography variant="caption" fontWeight={600} color="text.secondary" sx={{ display: "block" }}>AUC SCORE</Typography>
            </Box>
            <Box sx={{ textAlign: 'center', flex: 1, minWidth: 0 }}>
              <Typography variant="h4" color="error.main" fontWeight={900} sx={metricValueSx}>
                {aucThreshold}
              </Typography>
              <Typography variant="caption" fontWeight={600} color="text.secondary" sx={{ display: "block" }}>THRESHOLD</Typography>
            </Box>
          </Stack>
        </Paper>

        {detailData?.anomaly_config_params && (
          <Box>
            <Typography variant="caption" color="text.secondary" fontWeight={700}>MODEL CONFIGURATION</Typography>
            <Paper variant="outlined" sx={{ p: 2, mt: 1, bgcolor: '#ffffff', borderRadius: 3 }}>
              <Grid container spacing={2}>
                {Object.entries(detailData.anomaly_config_params).map(([k, v]) => {
                  const displayValue = formatConfigValue(v);

                  return (
                    <Grid item xs={12} sm={6} key={k} sx={{ minWidth: 0 }}>
                      <Typography
                        variant="caption"
                        color="text.secondary"
                        sx={{
                          display: 'block',
                          textTransform: 'uppercase',
                          fontSize: '0.65rem',
                          lineHeight: 1.3,
                        }}
                      >
                        {k.replace(/_/g, ' ')}
                      </Typography>
                      <Typography
                        variant="body2"
                        fontWeight={700}
                        title={String(v ?? '-')}
                        sx={{
                          maxWidth: '100%',
                          overflowWrap: 'anywhere',
                          wordBreak: 'break-word',
                          lineHeight: 1.35,
                        }}
                      >
                        {displayValue}
                      </Typography>
                    </Grid>
                  );
                })}
              </Grid>
            </Paper>
          </Box>
        )}
      </Grid>

      <Grid item xs={12} md={8}>
        <Typography variant="caption" color="text.secondary" fontWeight={700}>FEATURE IMPORTANCE (SHAP VALUES)</Typography>
        <Paper variant="outlined" sx={{ mt: 1, p: 2, borderRadius: 3, minHeight: 400 }}>
          {shapData.length > 0 ? (
            <ResponsiveContainer width="100%" height={shapChartHeight}>
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
