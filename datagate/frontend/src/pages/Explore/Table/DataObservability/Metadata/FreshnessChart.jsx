import React, { useMemo } from "react";
import { Box, Card, CardContent, Chip, Grid, Stack, Typography } from "@mui/material";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Area, ComposedChart, Legend,
} from "recharts";
import { format } from "date-fns";

const STATUS_CONFIG = {
  on_time: { label: "On Time", color: "success", emoji: "✅" },
  late: { label: "Late", color: "error", emoji: "🚨" },
};

function FreshnessChart({ snapshots = [], prediction }) {
  const status = prediction?.status || "on_time";
  const config = STATUS_CONFIG[status] || STATUS_CONFIG.on_time;

  const lagData = useMemo(() => {
    if (!snapshots.length) return [];
    return snapshots
      .filter((s) => s.last_updated_time)
      .map((s) => {
        const snapTime = new Date(s.snapshot_time);
        const updateTime = new Date(s.last_updated_time);
        const lagHours = Math.max(0, (snapTime - updateTime) / (1000 * 60 * 60));
        return {
          time: format(snapTime, "MM/dd HH:mm"),
          lag: parseFloat(lagHours.toFixed(1)),
        };
      })
      .reverse();
  }, [snapshots]);

  // Merge forecast with actual data for prediction band
  const forecastData = useMemo(() => {
    if (!prediction?.forecast?.length) return [];
    return prediction.forecast.map((f) => ({
      time: f.date ? format(new Date(f.date), "MM/dd HH:mm") : "",
      predicted: f.predicted_interval,
      lower: f.lower,
      upper: f.upper,
    }));
  }, [prediction]);

  return (
    <Stack spacing={3}>
      {/* Status Summary */}
      <Grid container spacing={2}>
        <Grid item xs={12} md={4}>
          <Card variant="outlined" sx={{ borderRadius: 2, borderColor: "#E6EBF2" }}>
            <CardContent>
              <Typography variant="caption" color="text.secondary" sx={{ textTransform: "uppercase", fontWeight: 600, letterSpacing: 0.5 }}>
                Freshness Status
              </Typography>
              <Stack direction="row" alignItems="center" spacing={1} sx={{ mt: 1 }}>
                <Typography sx={{ fontSize: 28 }}>{config.emoji}</Typography>
                <Chip label={config.label} color={config.color} size="small" sx={{ fontWeight: 700 }} />
              </Stack>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card variant="outlined" sx={{ borderRadius: 2, borderColor: "#E6EBF2" }}>
            <CardContent>
              <Typography variant="caption" color="text.secondary" sx={{ textTransform: "uppercase", fontWeight: 600, letterSpacing: 0.5 }}>
                Hours Since Last Update
              </Typography>
              <Typography sx={{ fontSize: 28, fontWeight: 700, mt: 1, color: status === "late" ? "#d32f2f" : "#2e7d32" }}>
                {prediction?.current_delay_hours != null ? `${prediction.current_delay_hours}h` : "—"}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card variant="outlined" sx={{ borderRadius: 2, borderColor: "#E6EBF2" }}>
            <CardContent>
              <Typography variant="caption" color="text.secondary" sx={{ textTransform: "uppercase", fontWeight: 600, letterSpacing: 0.5 }}>
                Predicted Max Delay
              </Typography>
              <Typography sx={{ fontSize: 28, fontWeight: 700, mt: 1 }}>
                {prediction?.predicted_max_delay != null ? `${prediction.predicted_max_delay}h` : "—"}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Freshness Lag Chart */}
      <Card variant="outlined" sx={{ borderRadius: 2, borderColor: "#E6EBF2" }}>
        <CardContent>
          <Typography variant="subtitle1" fontWeight={700} sx={{ mb: 2 }}>
            Freshness Lag Timeline
          </Typography>
          <Box sx={{ height: 320, width: "100%" }}>
            {lagData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={lagData}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                  <XAxis dataKey="time" fontSize={10} tickMargin={10} />
                  <YAxis fontSize={10} label={{ value: "Hours", angle: -90, position: "insideLeft", fontSize: 10 }} />
                  <Tooltip contentStyle={{ borderRadius: 8, border: "none", boxShadow: "0 4px 12px rgba(0,0,0,0.1)" }} />
                  <Legend />
                  <Line type="monotone" dataKey="lag" stroke="#3f51b5" strokeWidth={2.5} dot={{ r: 3, fill: "#3f51b5" }} name="Actual Lag (h)" />
                </ComposedChart>
              </ResponsiveContainer>
            ) : (
              <EmptyState message="No freshness data available. Run a metadata scan to start collecting." />
            )}
          </Box>
        </CardContent>
      </Card>

      {/* Prediction Band Chart */}
      {forecastData.length > 0 && (
        <Card variant="outlined" sx={{ borderRadius: 2, borderColor: "#E6EBF2" }}>
          <CardContent>
            <Typography variant="subtitle1" fontWeight={700} sx={{ mb: 2 }}>
              Prophet Freshness Prediction (95% CI)
            </Typography>
            <Box sx={{ height: 280, width: "100%" }}>
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={forecastData}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                  <XAxis dataKey="time" fontSize={10} tickMargin={10} />
                  <YAxis fontSize={10} />
                  <Tooltip contentStyle={{ borderRadius: 8, border: "none", boxShadow: "0 4px 12px rgba(0,0,0,0.1)" }} />
                  <Legend />
                  <Area type="monotone" dataKey="upper" stroke="none" fill="#e8eaf6" name="Upper Bound" />
                  <Area type="monotone" dataKey="lower" stroke="none" fill="#ffffff" name="Lower Bound" />
                  <Line type="monotone" dataKey="predicted" stroke="#7c4dff" strokeWidth={2} dot={false} name="Predicted" />
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

export default FreshnessChart;
