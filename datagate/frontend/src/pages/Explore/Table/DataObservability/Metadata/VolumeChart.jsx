import React, { useMemo } from "react";
import { Box, Card, CardContent, Grid, Stack, Typography } from "@mui/material";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, ComposedChart, Area, Line, Legend,
} from "recharts";

function VolumeChart({ volumeData = [], prediction }) {
  const chartData = useMemo(() => {
    return volumeData.map((v) => ({
      date: v.dt,
      records: v.records_added || 0,
    }));
  }, [volumeData]);

  const forecastData = useMemo(() => {
    if (!prediction?.forecast?.length) return [];
    const historyMap = {};
    (prediction.history || []).forEach((h) => {
      historyMap[h.date] = h.actual;
    });
    return prediction.forecast.map((f) => ({
      date: f.date,
      actual: historyMap[f.date] ?? null,
      predicted: f.predicted,
      lower: f.lower,
      upper: f.upper,
    }));
  }, [prediction]);

  // Stats
  const totalRecords = chartData.reduce((sum, d) => sum + d.records, 0);
  const avgRecords = chartData.length ? Math.round(totalRecords / chartData.length) : 0;
  const maxRecords = chartData.length ? Math.max(...chartData.map((d) => d.records)) : 0;

  return (
    <Stack spacing={3}>
      {/* Stats Cards */}
      <Grid container spacing={2}>
        <Grid item xs={12} md={4}>
          <Card variant="outlined" sx={{ borderRadius: 2, borderColor: "#E6EBF2" }}>
            <CardContent>
              <Typography variant="caption" color="text.secondary" sx={{ textTransform: "uppercase", fontWeight: 600, letterSpacing: 0.5 }}>
                Total Records Ingested
              </Typography>
              <Typography sx={{ fontSize: 28, fontWeight: 700, mt: 1, color: "#2e7d32" }}>
                {totalRecords.toLocaleString()}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card variant="outlined" sx={{ borderRadius: 2, borderColor: "#E6EBF2" }}>
            <CardContent>
              <Typography variant="caption" color="text.secondary" sx={{ textTransform: "uppercase", fontWeight: 600, letterSpacing: 0.5 }}>
                Daily Average
              </Typography>
              <Typography sx={{ fontSize: 28, fontWeight: 700, mt: 1 }}>
                {avgRecords.toLocaleString()}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card variant="outlined" sx={{ borderRadius: 2, borderColor: "#E6EBF2" }}>
            <CardContent>
              <Typography variant="caption" color="text.secondary" sx={{ textTransform: "uppercase", fontWeight: 600, letterSpacing: 0.5 }}>
                Peak Day
              </Typography>
              <Typography sx={{ fontSize: 28, fontWeight: 700, mt: 1, color: "#f57c00" }}>
                {maxRecords.toLocaleString()}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Volume Bar Chart */}
      <Card variant="outlined" sx={{ borderRadius: 2, borderColor: "#E6EBF2" }}>
        <CardContent>
          <Typography variant="subtitle1" fontWeight={700} sx={{ mb: 2 }}>
            Daily Ingestion Volume
          </Typography>
          <Box sx={{ height: 320, width: "100%" }}>
            {chartData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                  <XAxis dataKey="date" fontSize={10} tickMargin={10} />
                  <YAxis fontSize={10} tickFormatter={(v) => v >= 1000 ? `${(v / 1000).toFixed(0)}k` : v} />
                  <Tooltip
                    contentStyle={{ borderRadius: 8, border: "none", boxShadow: "0 4px 12px rgba(0,0,0,0.1)" }}
                    formatter={(value) => [value.toLocaleString(), "Records"]}
                  />
                  <Bar dataKey="records" fill="#4caf50" radius={[4, 4, 0, 0]} name="Records Added" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <EmptyState message="No volume data available. Run a metadata scan to start collecting." />
            )}
          </Box>
        </CardContent>
      </Card>

      {/* Prediction Chart */}
      {forecastData.length > 0 && (
        <Card variant="outlined" sx={{ borderRadius: 2, borderColor: "#E6EBF2" }}>
          <CardContent>
            <Typography variant="subtitle1" fontWeight={700} sx={{ mb: 2 }}>
              Prophet Volume Prediction (95% CI)
            </Typography>
            <Box sx={{ height: 280, width: "100%" }}>
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={forecastData}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                  <XAxis dataKey="date" fontSize={10} tickMargin={10} />
                  <YAxis fontSize={10} tickFormatter={(v) => v >= 1000 ? `${(v / 1000).toFixed(0)}k` : v} />
                  <Tooltip contentStyle={{ borderRadius: 8, border: "none", boxShadow: "0 4px 12px rgba(0,0,0,0.1)" }} />
                  <Legend />
                  <Area type="monotone" dataKey="upper" stroke="none" fill="#e8f5e9" name="Upper Bound" />
                  <Area type="monotone" dataKey="lower" stroke="none" fill="#ffffff" name="Lower Bound" />
                  <Line type="monotone" dataKey="predicted" stroke="#2e7d32" strokeWidth={2} strokeDasharray="5 5" dot={false} name="Predicted" />
                  <Bar dataKey="actual" fill="#4caf50" radius={[3, 3, 0, 0]} name="Actual" opacity={0.7} />
                </ComposedChart>
              </ResponsiveContainer>
            </Box>
          </CardContent>
        </Card>
      )}
    </Stack>
  );
}

function EmptyState({ message }) {
  return (
    <Box sx={{ display: "flex", alignItems: "center", justifyContent: "center", height: "100%", bgcolor: "#fafafa", borderRadius: 2 }}>
      <Typography color="text.secondary" variant="body2">{message}</Typography>
    </Box>
  );
}

export default VolumeChart;
