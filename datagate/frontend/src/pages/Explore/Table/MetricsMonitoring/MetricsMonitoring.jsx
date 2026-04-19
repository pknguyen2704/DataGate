import React, { useEffect, useState, useMemo } from "react";
import {
  Box,
  Card,
  CardContent,
  Chip,
  Grid,
  Stack,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Tooltip,
  CircularProgress,
} from "@mui/material";
import {
  Assessment as ChartIcon,
  CheckCircle as HealthyIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  ShowChart as TrendIcon,
} from "@mui/icons-material";
import { useDispatch, useSelector } from "react-redux";
import { fetchMetrics } from "~/stores/slices/exploreSlice/index";
import MetricDetailChart from "./MetricDetailChart";

function MetricsMonitoring({ assetDetail }) {
  const dispatch = useDispatch();
  const tableName = assetDetail?.table_name;
  const schemaName = assetDetail?.schema_name;
  const fullTableName = `${schemaName || "public"}.${tableName}`;

  const { metricsByTable, metricsStatusByTable } = useSelector(
    (state) => state.explore.observability
  );

  const [selectedMetric, setSelectedMetric] = useState(null);

  useEffect(() => {
    if (tableName) {
      dispatch(fetchMetrics({ tableName, schemaName }));
    }
  }, [dispatch, tableName, schemaName]);

  const metrics = metricsByTable[fullTableName] || [];
  const status = metricsStatusByTable[fullTableName];

  // Group metrics by column
  const metricsByColumn = useMemo(() => {
    const grouped = {};
    metrics.forEach((m) => {
      const col = m.column_name;
      if (!grouped[col]) grouped[col] = [];
      grouped[col].push(m);
    });
    return grouped;
  }, [metrics]);

  if (status === "loading" && !metrics.length) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", py: 10 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Stack spacing={3}>
      <Typography variant="h6" fontWeight={700}>
        Data Quality Metrics (pyDeequ)
      </Typography>

      <Grid container spacing={2}>
        {/* Metric Summary Cards */}
        <Grid item xs={12} md={4}>
          <Card variant="outlined" sx={{ borderRadius: 2 }}>
            <CardContent>
              <Typography variant="caption" color="text.secondary" fontWeight={600}>
                HEALTHY METRICS
              </Typography>
              <Stack direction="row" alignItems="center" spacing={1} sx={{ mt: 1 }}>
                <HealthyIcon color="success" />
                <Typography variant="h4" fontWeight={700}>
                  {Object.keys(metricsByColumn).length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Columns analyzed
                </Typography>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <TableContainer component={Paper} variant="outlined" sx={{ borderRadius: 2 }}>
        <Table size="small">
          <TableHead sx={{ bgcolor: "#f8f9fa" }}>
            <TableRow>
              <TableCell sx={{ fontWeight: 700 }}>Column</TableCell>
              <TableCell sx={{ fontWeight: 700 }}>Metric</TableCell>
              <TableCell sx={{ fontWeight: 700 }}>Value</TableCell>
              <TableCell sx={{ fontWeight: 700 }}>Last Measured</TableCell>
              <TableCell align="right" sx={{ fontWeight: 700 }}>Trend</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {Object.entries(metricsByColumn).map(([col, colMetrics]) => {
              // Only show the latest for each metric type in the main table
              const latestMetrics = {};
              colMetrics.forEach(m => {
                if (!latestMetrics[m.metric_name] || new Date(m.snapshot_time) > new Date(latestMetrics[m.metric_name].snapshot_time)) {
                  latestMetrics[m.metric_name] = m;
                }
              });

              return Object.values(latestMetrics).map((m, idx) => (
                <TableRow key={`${col}-${m.metric_name}`} hover>
                  {idx === 0 && (
                    <TableCell rowSpan={Object.keys(latestMetrics).length} sx={{ fontWeight: 600, verticalAlign: 'top', pt: 2 }}>
                      {col === '*' ? 'Table Level' : col}
                    </TableCell>
                  )}
                  <TableCell>{m.metric_name}</TableCell>
                  <TableCell>
                    <Typography fontWeight={600}>
                      {m.metric_name.includes('percentage') || m.metric_name.includes('Completeness') 
                        ? `${(m.metric_value * 100).toFixed(2)}%`
                        : m.metric_value.toLocaleString()}
                    </Typography>
                  </TableCell>
                  <TableCell color="text.secondary">
                    {new Date(m.snapshot_time).toLocaleString()}
                  </TableCell>
                  <TableCell align="right">
                    <IconButton 
                      size="small" 
                      onClick={() => setSelectedMetric({ column: col, metric: m.metric_name })}
                      color={selectedMetric?.column === col && selectedMetric?.metric === m.metric_name ? "primary" : "default"}
                    >
                      <ChartIcon fontSize="small" />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ));
            })}
          </TableBody>
        </Table>
      </TableContainer>

      {selectedMetric && (
        <MetricDetailChart 
          tableName={tableName}
          schemaName={schemaName}
          column={selectedMetric.column}
          metric={selectedMetric.metric}
          history={metrics.filter(m => m.column_name === selectedMetric.column && m.metric_name === selectedMetric.metric)}
        />
      )}
    </Stack>
  );
}

export default MetricsMonitoring;