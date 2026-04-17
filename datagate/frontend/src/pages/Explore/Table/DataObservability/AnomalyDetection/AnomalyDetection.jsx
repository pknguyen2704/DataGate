import React, { useEffect, useMemo, useState } from "react";
import {
  Alert,
  Box,
  Chip,
  CircularProgress,
  Grid,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import { mlQualityApi } from "~/apis/mlQuality";
import { datagateColors, panelSx, subtlePanelSx } from "~/theme";

const formatDateTime = (value) => {
  if (!value) return "--";
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return String(value);
  return parsed.toLocaleString();
};

function AnomalyDetection({ assetDetail }) {
  const latestMlRun = assetDetail?.latest_ml_run;
  const [runs, setRuns] = useState([]);
  const [selectedRunId, setSelectedRunId] = useState(null);
  const [selectedRunDetail, setSelectedRunDetail] = useState(null);
  const [loadingRuns, setLoadingRuns] = useState(false);
  const [loadingDetail, setLoadingDetail] = useState(false);

  useEffect(() => {
    if (!assetDetail?.table_name) return;

    const fetchRuns = async () => {
      try {
        setLoadingRuns(true);
        const response = await mlQualityApi.getRuns(assetDetail.table_name);
        const nextRuns = response.data || [];
        setRuns(nextRuns);
        setSelectedRunId(nextRuns[0]?.id || null);
      } catch (error) {
        console.error("Failed to fetch ML runs", error);
        setRuns([]);
      } finally {
        setLoadingRuns(false);
      }
    };

    fetchRuns();
  }, [assetDetail?.table_name]);

  useEffect(() => {
    if (!selectedRunId) {
      setSelectedRunDetail(null);
      return;
    }

    const fetchRunDetail = async () => {
      try {
        setLoadingDetail(true);
        const response = await mlQualityApi.getRunDetail(selectedRunId);
        setSelectedRunDetail(response.data);
      } catch (error) {
        console.error("Failed to fetch ML run detail", error);
        setSelectedRunDetail(null);
      } finally {
        setLoadingDetail(false);
      }
    };

    fetchRunDetail();
  }, [selectedRunId]);

  const clusterGroups = useMemo(
    () => selectedRunDetail?.raw_json?.cluster_groups || [],
    [selectedRunDetail?.raw_json?.cluster_groups]
  );
  const rowExplanations = useMemo(
    () => selectedRunDetail?.raw_json?.row_explanations || [],
    [selectedRunDetail?.raw_json?.row_explanations]
  );
  const driftMetrics = selectedRunDetail?.raw_json?.drift_metrics || null;
  const specificity = selectedRunDetail?.raw_json?.specificity || null;
  const excludedTimeColumns = selectedRunDetail?.raw_json?.excluded_time_columns || [];

  return (
    <Stack spacing={3}>
      <Alert severity="info">
        Pillar 4 uses unsupervised ML with weekday-aware historical baselines, random sampling, and grouped anomalous
        columns to reduce alert fatigue while surfacing unknown distribution shifts.
      </Alert>

      <Grid container spacing={2}>
        <MetricCard label="Latest Status" value={latestMlRun?.status || "--"} />
        <MetricCard label="Latest Score" value={latestMlRun?.anomaly_score ?? "--"} />
        <MetricCard label="Latest Run" value={formatDateTime(latestMlRun?.batch_time)} />
      </Grid>

      {selectedRunDetail?.raw_json ? (
        <Grid container spacing={2}>
          <MetricCard label="Impacted Ratio" value={driftMetrics?.impacted_ratio != null ? `${(driftMetrics.impacted_ratio * 100).toFixed(2)}%` : "--"} />
          <MetricCard label="Drift Gap" value={driftMetrics?.drift_gap != null ? driftMetrics.drift_gap.toFixed(4) : "--"} />
          <MetricCard label="Dynamic Threshold" value={specificity?.dynamic_threshold != null ? specificity.dynamic_threshold.toFixed(4) : "--"} />
        </Grid>
      ) : null}

      <Grid container spacing={3}>
        <Grid item xs={12} lg={4}>
          <Paper sx={{ ...panelSx, p: 3, height: "100%" }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              ML Run History
            </Typography>

            {loadingRuns ? (
              <CircularProgress size={24} />
            ) : runs.length === 0 ? (
              <Typography color="text.secondary">No ML anomaly runs have been recorded for this table yet.</Typography>
            ) : (
              <Stack spacing={1.5}>
                {runs.map((run) => (
                  <Box
                    key={run.id}
                    onClick={() => setSelectedRunId(run.id)}
                    sx={{
                      p: 2,
                      border: "1px solid",
                      borderColor: run.id === selectedRunId ? "primary.main" : "divider",
                      borderRadius: 2,
                      cursor: "pointer",
                      backgroundColor: run.id === selectedRunId ? datagateColors.selectedBackground : datagateColors.cardBackground,
                    }}
                  >
                    <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 0.75 }}>
                      <Typography sx={{ fontWeight: 700 }}>{formatDateTime(run.batch_time)}</Typography>
                      <Chip size="small" color={run.status === "ALERT" ? "warning" : "success"} label={run.status} />
                    </Stack>
                    <Typography variant="body2" color="text.secondary">
                      Effective partition: {run.partition_key || "--"}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Score: {run.anomaly_score ?? "--"}
                    </Typography>
                  </Box>
                ))}
              </Stack>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} lg={8}>
          <Paper sx={{ ...panelSx, p: 3, mb: 3 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Top Anomalous Columns
            </Typography>

            {loadingDetail ? (
              <CircularProgress size={24} />
            ) : !selectedRunDetail ? (
              <Typography color="text.secondary">Select a run to inspect anomalous columns.</Typography>
            ) : selectedRunDetail.features?.length === 0 ? (
              <Typography color="text.secondary">No feature importance information is available for this run.</Typography>
            ) : (
              <TableContainer>
                <Table size="small">
                  <TableHead sx={{ bgcolor: datagateColors.tableHeadBackground }}>
                    <TableRow>
                      <TableCell>Column</TableCell>
                      <TableCell>Importance Score</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {selectedRunDetail.features.map((feature) => (
                      <TableRow key={`${selectedRunDetail.id}-${feature.id}`}>
                        <TableCell sx={{ fontWeight: 600 }}>{feature.column_name}</TableCell>
                        <TableCell>{feature.importance_score.toFixed(4)}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </Paper>

          <Paper sx={{ ...panelSx, p: 3 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Clustered Impact Groups
            </Typography>

            {!selectedRunDetail ? (
              <Typography color="text.secondary">Select a run to view grouped impact clusters.</Typography>
            ) : clusterGroups.length === 0 ? (
              <Typography color="text.secondary">No grouped anomaly clusters were generated for this run.</Typography>
            ) : (
              <Stack spacing={1.5}>
                {clusterGroups.map((group, index) => (
                  <Box key={`${selectedRunDetail.id}-cluster-${index}`} sx={{ ...subtlePanelSx, p: 2 }}>
                    <Typography sx={{ fontWeight: 700, mb: 1 }}>Cluster {index + 1}</Typography>
                    <Stack direction="row" spacing={1} flexWrap="wrap">
                      {group.map((column) => (
                        <Chip key={`${selectedRunDetail.id}-${index}-${column}`} label={column} />
                      ))}
                    </Stack>
                  </Box>
                ))}
              </Stack>
            )}

            {selectedRunDetail?.raw_json ? (
              <Box sx={{ ...subtlePanelSx, mt: 3, p: 2 }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1 }}>
                  Run Settings
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Effective date: {selectedRunDetail.raw_json.effective_date || "--"} | Sample size:{" "}
                  {selectedRunDetail.raw_json.sample_size || "--"} | Sensitivity:{" "}
                  {selectedRunDetail.raw_json.sensitivity || "--"} | Seasonality:{" "}
                  {selectedRunDetail.raw_json.seasonality_mode || "--"}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  Excluded time columns: {excludedTimeColumns.length ? excludedTimeColumns.join(", ") : "--"}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  Reference noise: {specificity?.reference_noise != null ? specificity.reference_noise.toFixed(4) : "--"} |
                  Current center: {driftMetrics?.current_center != null ? ` ${driftMetrics.current_center.toFixed(4)}` : " --"} |
                  Min impacted ratio: {driftMetrics?.min_impacted_ratio != null ? ` ${(driftMetrics.min_impacted_ratio * 100).toFixed(2)}%` : " --"}
                </Typography>
              </Box>
            ) : null}
          </Paper>

          <Paper sx={{ ...panelSx, p: 3, mt: 3 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              SHAP Row Explanations
            </Typography>

            {!selectedRunDetail ? (
              <Typography color="text.secondary">Select a run to inspect row-level explanations.</Typography>
            ) : rowExplanations.length === 0 ? (
              <Typography color="text.secondary">No row-level SHAP explanations were generated for this run.</Typography>
            ) : (
              <Stack spacing={1.5}>
                {rowExplanations.map((row) => (
                  <Box key={`${selectedRunDetail.id}-row-${row.row_rank}`} sx={{ ...subtlePanelSx, p: 2 }}>
                    <Typography sx={{ fontWeight: 700, mb: 1 }}>
                      Row {row.row_rank} · score {row.row_score?.toFixed?.(4) ?? row.row_score}
                    </Typography>
                    <Stack spacing={1}>
                      {row.top_columns?.map((column) => (
                        <Typography key={`${selectedRunDetail.id}-${row.row_rank}-${column.column_name}`} variant="body2" color="text.secondary">
                          {column.column_name}: {column.importance_score?.toFixed?.(4) ?? column.importance_score} via {column.top_feature} | value: {column.cell_value ?? "--"}
                        </Typography>
                      ))}
                    </Stack>
                  </Box>
                ))}
              </Stack>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Stack>
  );
}

function MetricCard({ label, value }) {
  return (
    <Grid item xs={12} md={4}>
      <Paper sx={{ ...panelSx, p: 2.5 }}>
        <Typography variant="caption" color="text.secondary" fontWeight={700}>
          {label}
        </Typography>
        <Typography variant="h6" fontWeight={800} sx={{ mt: 0.5 }}>
          {typeof value === "number" ? value.toLocaleString() : value}
        </Typography>
      </Paper>
    </Grid>
  );
}

export default AnomalyDetection;
