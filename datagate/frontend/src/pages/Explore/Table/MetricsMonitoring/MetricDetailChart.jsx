import React, { useEffect, useState, useMemo } from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Stack,
  CircularProgress,
} from "@mui/material";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  ComposedChart,
  Legend,
} from "recharts";
import { format } from "date-fns";
import { observabilityApi } from "~/apis/observability";

function MetricDetailChart({ tableName, schemaName, column, metric, history }) {
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function fetchPrediction() {
      setLoading(true);
      try {
        const response = await observabilityApi.getMetricPredictions({
          table: tableName,
          schema: schemaName || null,
          column: column,
          metric: metric,
        });
        setPrediction(response.data);
      } catch (error) {
        console.error("Failed to fetch metric prediction", error);
      } finally {
        setLoading(false);
      }
    }
    fetchPrediction();
  }, [tableName, schemaName, column, metric]);

  const chartData = useMemo(() => {
    // Combine actual history with forecast
    const actuals = history.map(h => ({
      time: new Date(h.snapshot_time).getTime(),
      displayTime: format(new Date(h.snapshot_time), "MM/dd HH:mm"),
      actual: h.metric_value,
    })).sort((a, b) => a.time - b.time);

    if (!prediction || prediction.status !== "success") return actuals;

    const forecast = prediction.forecast.map(f => ({
      time: new Date(f.ds).getTime(),
      displayTime: format(new Date(f.ds), "MM/dd HH:mm"),
      predicted: f.yhat,
      lower: f.yhat_lower,
      upper: f.yhat_upper,
    }));

    // Merge actuals and forecast by time
    const allTimes = Array.from(new Set([...actuals.map(a => a.time), ...forecast.map(f => f.time)])).sort((a, b) => a - b);
    
    return allTimes.map(t => {
      const a = actuals.find(act => act.time === t);
      const f = forecast.find(foc => foc.time === t);
      return {
        ...(a || {}),
        ...(f || {}),
        displayTime: format(new Date(t), "MM/dd HH:mm"),
      };
    });
  }, [history, prediction]);

  return (
    <Card variant="outlined" sx={{ borderRadius: 2, mt: 2 }}>
      <CardContent>
        <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
          <Box>
            <Typography variant="subtitle1" fontWeight={700}>
              {column === '*' ? 'Table' : column} - {metric}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Historical values and Prophet prediction (95% CI)
            </Typography>
          </Box>
          {loading && <CircularProgress size={20} />}
        </Stack>

        <Box sx={{ height: 350, width: "100%" }}>
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
              <XAxis 
                dataKey="displayTime" 
                fontSize={10} 
                tickMargin={10} 
                minTickGap={30}
              />
              <YAxis 
                fontSize={10} 
                domain={['auto', 'auto']}
              />
              <Tooltip 
                contentStyle={{ borderRadius: 8, border: "none", boxShadow: "0 4px 12px rgba(0,0,0,0.1)" }} 
              />
              <Legend />
              <Area 
                type="monotone" 
                dataKey="upper" 
                stroke="none" 
                fill="#e8eaf6" 
                name="Confidence Upper" 
              />
              <Area 
                type="monotone" 
                dataKey="lower" 
                stroke="none" 
                fill="#ffffff" 
                name="Confidence Lower" 
              />
              <Line 
                type="monotone" 
                dataKey="actual" 
                stroke="#3f51b5" 
                strokeWidth={2.5} 
                dot={{ r: 3, fill: "#3f51b5" }} 
                name="Actual Value" 
              />
              <Line 
                type="monotone" 
                dataKey="predicted" 
                stroke="#7c4dff" 
                strokeWidth={2} 
                strokeDasharray="5 5" 
                dot={false} 
                name="Predicted" 
              />
            </ComposedChart>
          </ResponsiveContainer>
        </Box>
      </CardContent>
    </Card>
  );
}

export default MetricDetailChart;
