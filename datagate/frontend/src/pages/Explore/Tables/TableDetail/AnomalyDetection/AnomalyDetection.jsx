import React from "react";
import {
  Alert,
  Chip,
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
import {
  AutoGraphOutlined as TrendIcon,
  InsightsOutlined as InsightsIcon,
  ReportProblemOutlined as AlertIcon,
} from "@mui/icons-material";
import { tablesApi } from "~/apis/api";
import { panelSx, subtlePanelSx } from "~/theme";

const formatAnomalyDetail = (row) => {
  if (row.message) return row.message;

  const firstRootCause = row.root_causes?.[0];
  if (firstRootCause) {
    if (firstRootCause.category === "profiling" || firstRootCause.category === "metadata") {
      const identifier = firstRootCause.column_name
        ? `${firstRootCause.column_name}.${firstRootCause.metric_name}`
        : firstRootCause.metric_name;
      return `${identifier}: actual ${firstRootCause.actual}, expected ${firstRootCause.expected}`;
    }
    if (firstRootCause.column_name && firstRootCause.segment_value) {
      return `${firstRootCause.column_name}=${firstRootCause.segment_value}`;
    }
  }

  const severitySummary = Object.entries(row.severity_counts || {})
    .map(([key, value]) => `${key}:${value}`)
    .join(", ");

  return severitySummary ? `severity ${severitySummary}` : "--";
};

function AnomalyDetection({ tableId, assetDetail }) {
  const [anomalyRows, setAnomalyRows] = React.useState([]);
  const [error, setError] = React.useState(null);

  React.useEffect(() => {
    if (!tableId) return;
    tablesApi.getAnomalies(tableId, { limit: 12 })
      .then((response) => {
        setAnomalyRows(response.data || []);
      })
      .catch((err) => setError(err?.response?.data?.detail || "Could not load anomaly signals."));
  }, [tableId]);

  const detectedRows = anomalyRows.filter((row) => row.status === "anomaly_detected");
  const totalSignals = detectedRows.reduce((sum, row) => sum + (row.anomaly_count || 0), 0);
  const latestRows = anomalyRows.slice(0, 5);
  const highestAuc = anomalyRows.reduce((max, row) => Math.max(max, row.auc || 0), 0);

  return (
    <Stack spacing={3}>
      <Paper
        sx={{
          ...panelSx,
          p: 3,
          background:
            "linear-gradient(135deg, rgba(16, 185, 129, 0.12) 0%, rgba(255, 255, 255, 0.94) 42%, rgba(248, 250, 252, 1) 100%)",
        }}
      >
        <Stack spacing={1.5}>
          <Stack direction="row" spacing={1.5} alignItems="center">
            <InsightsIcon color="primary" />
            <Typography variant="h5" fontWeight={800}>Anomaly signals</Typography>
          </Stack>
          <Typography color="text.secondary">
            This surface shows persisted anomaly detection runs for {assetDetail?.full_name || assetDetail?.table_name}, including score, severity distribution, and root-cause hints.
          </Typography>
        </Stack>
      </Paper>

      {error ? <Alert severity="warning">{error}</Alert> : null}

      <Stack direction={{ xs: "column", xl: "row" }} spacing={2}>
        <Paper sx={{ ...subtlePanelSx, p: 2.5, flex: 1 }}>
          <Stack direction="row" spacing={1.5} alignItems="center">
            <AlertIcon color="error" />
            <Stack spacing={0.5}>
              <Typography variant="overline" color="text.secondary">Detected runs</Typography>
              <Typography variant="h4" fontWeight={800}>{detectedRows.length}</Typography>
            </Stack>
          </Stack>
        </Paper>
        <Paper sx={{ ...subtlePanelSx, p: 2.5, flex: 1 }}>
          <Stack direction="row" spacing={1.5} alignItems="center">
            <TrendIcon color="warning" />
            <Stack spacing={0.5}>
              <Typography variant="overline" color="text.secondary">Anomalous rows</Typography>
              <Typography variant="h4" fontWeight={800}>{totalSignals}</Typography>
            </Stack>
          </Stack>
        </Paper>
        <Paper sx={{ ...subtlePanelSx, p: 2.5, flex: 1 }}>
          <Stack spacing={0.5}>
            <Typography variant="overline" color="text.secondary">Highest AUC</Typography>
            <Typography variant="h4" fontWeight={800}>{highestAuc.toFixed(3)}</Typography>
          </Stack>
        </Paper>
      </Stack>

      <Paper sx={{ ...panelSx, p: 3 }}>
        <Stack spacing={2}>
          <Typography variant="h6" fontWeight={800}>Latest anomaly runs</Typography>
          {latestRows.length === 0 ? (
            <Typography color="text.secondary">
              No anomaly results are stored yet. Run the anomaly detection job to populate this view.
            </Typography>
          ) : (
            latestRows.map((row) => (
              <Stack
                key={row.id}
                direction={{ xs: "column", lg: "row" }}
                spacing={1.5}
                justifyContent="space-between"
                sx={{ ...subtlePanelSx, p: 2 }}
              >
                <Stack spacing={0.75}>
                  <Typography fontWeight={700}>{row.target_date}</Typography>
                  <Typography color="text.secondary">
                    Date column: {row.date_column} • batch {row.batch_date_hour}
                  </Typography>
                </Stack>
                <Stack direction="row" spacing={1} flexWrap="wrap" alignItems="center">
                  <Chip size="small" label={`auc ${Number(row.auc || 0).toFixed(3)}`} />
                  <Chip size="small" color="primary" label={`rows ${row.anomaly_count ?? 0}`} />
                  <Chip
                    size="small"
                    color={row.status === "anomaly_detected" ? "error" : row.status === "skipped" ? "warning" : "success"}
                    label={row.status}
                  />
                </Stack>
              </Stack>
            ))
          )}
        </Stack>
      </Paper>

      <Paper sx={{ ...panelSx, overflow: "hidden" }}>
        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Batch</TableCell>
                <TableCell>Date</TableCell>
                <TableCell>AUC</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Detail</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {anomalyRows.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} align="center" sx={{ py: 7, color: "text.secondary" }}>
                    No anomaly signals yet. Results will appear here after the anomaly job writes to the database.
                  </TableCell>
                </TableRow>
              ) : (
                anomalyRows.map((row) => (
                  <TableRow key={row.id} hover>
                    <TableCell>{row.batch_date_hour}</TableCell>
                    <TableCell sx={{ fontWeight: 700 }}>{row.target_date}</TableCell>
                    <TableCell>{Number(row.auc || 0).toFixed(3)}</TableCell>
                    <TableCell>
                      <Chip
                        size="small"
                        color={row.status === "anomaly_detected" ? "error" : row.status === "skipped" ? "warning" : "success"}
                        label={row.status}
                      />
                    </TableCell>
                    <TableCell>
                      {formatAnomalyDetail(row)}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Stack>
  );
}

export default AnomalyDetection;
