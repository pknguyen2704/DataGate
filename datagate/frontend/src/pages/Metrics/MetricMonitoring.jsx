import React, { useEffect, useMemo, useState } from "react";
import {
  Alert,
  Box,
  Chip,
  CircularProgress,
  FormControl,
  Grid,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Slider,
  Stack,
  Typography,
} from "@mui/material";
import {
  AssessmentOutlined as MetricsIcon,
  InsightsOutlined as InsightsIcon,
  QueryStatsOutlined as StatsIcon,
  TuneOutlined as TuneIcon,
} from "@mui/icons-material";
import {
  Area,
  CartesianGrid,
  ComposedChart,
  Legend,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { useDispatch, useSelector } from "react-redux";
import { fetchAssets } from "~/stores/slices/servicesSlice";
import {
  fetchMonitoringRecommendations,
  fetchMonitoringSeries,
} from "~/stores/slices/monitoringSlice";

const CONFIDENCE_MARKS = [
  { value: 80, label: "80%" },
  { value: 95, label: "95%" },
  { value: 99, label: "99%" },
];

const formatMetricValue = (metric, value) => {
  if (value === null || value === undefined || Number.isNaN(value)) return "--";
  if (metric === "null_rate") return `${(value * 100).toFixed(2)}%`;
  return Number(value).toLocaleString(undefined, { maximumFractionDigits: 2 });
};

function MetricMonitoring() {
  const dispatch = useDispatch();
  const assets = useSelector((state) => state.services.assets);
  const assetsStatus = useSelector((state) => state.services.assetsStatus);
  const [selectedTable, setSelectedTable] = useState("");
  const [selectedColumn, setSelectedColumn] = useState("");
  const [selectedMetric, setSelectedMetric] = useState("null_rate");
  const [confidence, setConfidence] = useState(95);
  const resolvedSelectedTable = selectedTable || assets[0]?.table_name || "";

  const recommendations = useSelector(
    (state) => state.monitoring.recommendationsByTable[resolvedSelectedTable] || []
  );
  const recommendationsStatus = useSelector(
    (state) => state.monitoring.recommendationsStatusByTable[resolvedSelectedTable] || "idle"
  );
  const recommendationsError = useSelector(
    (state) => state.monitoring.recommendationsErrorByTable[resolvedSelectedTable] || ""
  );
  const resolvedSelectedColumn = recommendations.some((item) => item.column_name === selectedColumn)
    ? selectedColumn
    : recommendations[0]?.column_name || "";
  const selectedColumnConfig = recommendations.find(
    (item) => item.column_name === resolvedSelectedColumn
  ) || null;
  const resolvedSelectedMetric = selectedColumnConfig?.metrics?.some(
    (item) => item.metric === selectedMetric
  )
    ? selectedMetric
    : selectedColumnConfig?.metrics?.[0]?.metric || "null_rate";
  const seriesKey =
    resolvedSelectedTable && resolvedSelectedColumn && resolvedSelectedMetric
      ? `${resolvedSelectedTable}:${resolvedSelectedColumn}:${resolvedSelectedMetric}:${confidence}`
      : "";
  const rawSeries = useSelector((state) =>
    seriesKey ? state.monitoring.seriesByKey[seriesKey] || [] : []
  );
  const seriesStatus = useSelector((state) =>
    seriesKey ? state.monitoring.seriesStatusByKey[seriesKey] || "idle" : "idle"
  );
  const seriesError = useSelector((state) =>
    seriesKey ? state.monitoring.seriesErrorByKey[seriesKey] || "" : ""
  );

  useEffect(() => {
    if (assetsStatus === "idle") {
      dispatch(fetchAssets());
    }
  }, [assetsStatus, dispatch]);

  useEffect(() => {
    if (!resolvedSelectedTable) return;
    if (recommendationsStatus === "idle") {
      dispatch(fetchMonitoringRecommendations(resolvedSelectedTable));
    }
  }, [dispatch, recommendationsStatus, resolvedSelectedTable]);

  useEffect(() => {
    if (!resolvedSelectedTable || !resolvedSelectedColumn || !resolvedSelectedMetric) return;
    if (seriesStatus === "idle") {
      dispatch(
        fetchMonitoringSeries({
          tableName: resolvedSelectedTable,
          columnName: resolvedSelectedColumn,
          metric: resolvedSelectedMetric,
          confidence,
        })
      );
    }
  }, [confidence, dispatch, resolvedSelectedColumn, resolvedSelectedMetric, resolvedSelectedTable, seriesStatus]);

  const series = useMemo(
    () =>
      rawSeries.map((point) => ({
        ...point,
        date: new Date(point.created_at).toLocaleDateString("en-US", {
          month: "short",
          day: "numeric",
        }),
      })),
    [rawSeries]
  );

  const loadingAssets = assetsStatus === "loading";
  const loadingRecommendations = recommendationsStatus === "loading";
  const loadingSeries = seriesStatus === "loading";
  const error =
    assetsStatus === "failed"
      ? "Could not load data assets for metric monitoring."
      : seriesError || recommendationsError || "";

  const totalAnomalies = series.filter((point) => point.is_anomaly).length;

  return (
    <Box sx={{ p: 4, height: "100%", overflow: "auto", background: "#F6F8FC" }}>
      <Paper
        sx={{
          mb: 3,
          p: 4,
          borderRadius: 4,
          background: "linear-gradient(135deg, #0F1F4D 0%, #17397A 48%, #2E6BFF 100%)",
          color: "#FFFFFF",
          overflow: "hidden",
          position: "relative",
        }}
      >
        <Stack direction={{ xs: "column", lg: "row" }} spacing={3} justifyContent="space-between">
          <Box sx={{ maxWidth: 760 }}>
            <Typography variant="overline" sx={{ letterSpacing: "0.18em", opacity: 0.8 }}>
              Pillar 3
            </Typography>
            <Typography variant="h3" sx={{ fontWeight: 800, mb: 1.5, letterSpacing: "-0.03em" }}>
              Metric Monitoring
            </Typography>
            <Typography sx={{ fontSize: "1.05rem", opacity: 0.9, maxWidth: 720 }}>
              Monitor aggregate statistics such as null rate, mean, minimum, maximum, and standard deviation to detect slow-moving distribution drift. Confidence bands adapt to the selected sensitivity and the backend uses seasonal historical baselines for cleaner alerts.
            </Typography>
          </Box>

          <Stack spacing={1.5} sx={{ minWidth: { lg: 280 } }}>
            <Chip sx={{ color: "#fff", borderColor: "rgba(255,255,255,0.22)" }} variant="outlined" label="Confidence bands on every chart" />
            <Chip sx={{ color: "#fff", borderColor: "rgba(255,255,255,0.22)" }} variant="outlined" label="Sensitivity tuning: 80% / 95% / 99%" />
            <Chip sx={{ color: "#fff", borderColor: "rgba(255,255,255,0.22)" }} variant="outlined" label="Recommended metrics from profiling history" />
          </Stack>
        </Stack>
      </Paper>

      {error ? (
        <Alert severity="info" sx={{ mb: 3 }}>
          {error}
        </Alert>
      ) : null}

      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={4}>
          <MetricCard
            icon={<MetricsIcon />}
            label="Monitored assets"
            value={loadingAssets ? "--" : assets.length.toLocaleString()}
            helper="Assets accessible from your RBAC scope"
          />
        </Grid>
        <Grid item xs={12} md={4}>
          <MetricCard
            icon={<InsightsIcon />}
            label="Suggested columns"
            value={loadingRecommendations ? "--" : recommendations.length.toLocaleString()}
            helper="Auto-selected important columns from the latest profiling run"
          />
        </Grid>
        <Grid item xs={12} md={4}>
          <MetricCard
            icon={<StatsIcon />}
            label="Detected anomalies"
            value={loadingSeries ? "--" : totalAnomalies.toLocaleString()}
            helper={`At ${confidence}% confidence for the selected metric`}
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} lg={4}>
          <Paper sx={{ p: 3, borderRadius: 4, height: "100%" }}>
            <Typography variant="h6" sx={{ fontWeight: 700, mb: 2.5 }}>
              Monitoring Controls
            </Typography>

            {loadingAssets ? (
              <CircularProgress size={24} />
            ) : (
              <Stack spacing={2.5}>
                <FormControl fullWidth>
                  <InputLabel>Asset</InputLabel>
                  <Select label="Asset" value={resolvedSelectedTable} onChange={(event) => setSelectedTable(event.target.value)}>
                    {assets.map((asset) => (
                      <MenuItem key={`${asset.service_id}-${asset.table_name}`} value={asset.table_name}>
                        {asset.table_name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>

                <FormControl fullWidth disabled={loadingRecommendations || recommendations.length === 0}>
                  <InputLabel>Column</InputLabel>
                  <Select label="Column" value={resolvedSelectedColumn} onChange={(event) => setSelectedColumn(event.target.value)}>
                    {recommendations.map((column) => (
                      <MenuItem key={column.column_name} value={column.column_name}>
                        {column.column_name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>

                <FormControl fullWidth disabled={!selectedColumnConfig}>
                  <InputLabel>Metric</InputLabel>
                  <Select label="Metric" value={resolvedSelectedMetric} onChange={(event) => setSelectedMetric(event.target.value)}>
                    {(selectedColumnConfig?.metrics || []).map((metric) => (
                      <MenuItem key={metric.metric} value={metric.metric}>
                        {metric.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>

                <Box sx={{ px: 1 }}>
                  <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
                    <TuneIcon fontSize="small" color="primary" />
                    <Typography sx={{ fontWeight: 700 }}>Sensitivity tuning</Typography>
                  </Stack>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    Lower confidence produces tighter bands and more alerts. Higher confidence reduces noise.
                  </Typography>
                  <Slider
                    value={confidence}
                    onChange={(_, nextValue) => setConfidence(nextValue)}
                    step={null}
                    marks={CONFIDENCE_MARKS}
                    min={80}
                    max={99}
                  />
                </Box>

                <Box sx={{ p: 2.5, borderRadius: 3, bgcolor: "#F8FAFC", border: "1px solid #E5EAF2" }}>
                  <Typography sx={{ fontWeight: 700, mb: 1 }}>Backend behavior</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Daily metric results are persisted in PostgreSQL. Confidence bands are generated from historical profiling data with a seasonality-aware baseline by weekday before alerting on drift.
                  </Typography>
                </Box>
              </Stack>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} lg={8}>
          <Paper sx={{ p: 3, borderRadius: 4, mb: 3 }}>
            <Stack
              direction={{ xs: "column", md: "row" }}
              spacing={2}
              justifyContent="space-between"
              alignItems={{ xs: "flex-start", md: "center" }}
              sx={{ mb: 3 }}
            >
              <Box>
                <Typography variant="h6" sx={{ fontWeight: 700 }}>
                  Metric Chart with Confidence Interval
                </Typography>
                <Typography color="text.secondary">
                  {resolvedSelectedColumn ? `${resolvedSelectedColumn} · ${resolvedSelectedMetric}` : "Select an asset, column, and metric"}
                </Typography>
              </Box>
              <Stack direction="row" spacing={1}>
                <Chip label={`Confidence ${confidence}%`} color="primary" variant="outlined" />
                <Chip label={`${series.length} points`} variant="outlined" />
              </Stack>
            </Stack>

            <Box sx={{ height: 420 }}>
              {loadingSeries ? (
                <Stack alignItems="center" justifyContent="center" sx={{ height: "100%" }}>
                  <CircularProgress />
                </Stack>
              ) : series.length === 0 ? (
                <Stack alignItems="center" justifyContent="center" sx={{ height: "100%" }}>
                  <Typography color="text.secondary">No metric history is available for this selection.</Typography>
                </Stack>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <ComposedChart data={series}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#E8EDF5" vertical={false} />
                    <XAxis dataKey="date" axisLine={false} tickLine={false} />
                    <YAxis axisLine={false} tickLine={false} />
                    <Tooltip />
                    <Legend />
                    <Area
                      type="monotone"
                      dataKey="upper_bound"
                      stroke="none"
                      fill="#2E6BFF"
                      fillOpacity={0.12}
                      name="Upper bound"
                    />
                    <Area
                      type="monotone"
                      dataKey="lower_bound"
                      stroke="none"
                      fill="#FFFFFF"
                      fillOpacity={1}
                      name="Lower bound"
                    />
                    <Line type="monotone" dataKey="expected" stroke="#94A3B8" strokeDasharray="6 4" dot={false} name="Expected" />
                    <Line type="monotone" dataKey="value" stroke="#1D4ED8" strokeWidth={3} name="Actual" />
                  </ComposedChart>
                </ResponsiveContainer>
              )}
            </Box>
          </Paper>

          <Paper sx={{ p: 3, borderRadius: 4 }}>
            <Typography variant="h6" sx={{ fontWeight: 700, mb: 2.5 }}>
              Auto-suggested Metrics
            </Typography>

            {loadingRecommendations ? (
              <CircularProgress size={24} />
            ) : recommendations.length === 0 ? (
              <Typography color="text.secondary">
                Profiling history is required before suggested metrics can be generated.
              </Typography>
            ) : (
              <Grid container spacing={2}>
                {recommendations.map((column) => (
                  <Grid item xs={12} md={6} key={column.column_name}>
                    <Paper
                      variant="outlined"
                      sx={{
                        p: 2.5,
                        borderRadius: 3,
                        borderColor: column.column_name === resolvedSelectedColumn ? "#2E6BFF" : "#E5EAF2",
                        cursor: "pointer",
                      }}
                      onClick={() => {
                        setSelectedColumn(column.column_name);
                        setSelectedMetric(column.metrics[0]?.metric || "null_rate");
                      }}
                    >
                      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1.5 }}>
                        <Typography sx={{ fontWeight: 700 }}>{column.column_name}</Typography>
                        <Chip size="small" label={column.data_type || "--"} variant="outlined" />
                      </Stack>
                      <Stack spacing={1}>
                        {column.metrics.map((metric) => (
                          <Stack key={`${column.column_name}-${metric.metric}`} direction="row" justifyContent="space-between">
                            <Typography color="text.secondary">{metric.label}</Typography>
                            <Typography sx={{ fontWeight: 700 }}>{formatMetricValue(metric.metric, metric.value)}</Typography>
                          </Stack>
                        ))}
                      </Stack>
                    </Paper>
                  </Grid>
                ))}
              </Grid>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

function MetricCard({ icon, label, value, helper }) {
  return (
    <Paper sx={{ p: 3, borderRadius: 4, height: "100%" }}>
      <Stack direction="row" spacing={1.5} alignItems="center" sx={{ mb: 2 }}>
        <Box
          sx={{
            width: 44,
            height: 44,
            borderRadius: 2.5,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            bgcolor: "#E8F0FF",
            color: "#1D4ED8",
          }}
        >
          {icon}
        </Box>
        <Typography color="text.secondary">{label}</Typography>
      </Stack>
      <Typography sx={{ fontSize: "2.1rem", fontWeight: 800, letterSpacing: "-0.03em", mb: 0.5 }}>{value}</Typography>
      <Typography color="text.secondary">{helper}</Typography>
    </Paper>
  );
}

export default MetricMonitoring;
