import React from "react";
import {
  Alert,
  Chip,
  MenuItem,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";
import { rulesApi } from "~/apis/api";
import { datagateColors, panelSx, subtlePanelSx } from "~/theme";

const statusColorMap = {
  passed: "success",
  failed: "error",
  error: "warning",
};

function RuleVerification({ tableId }) {
  const [results, setResults] = React.useState([]);
  const [error, setError] = React.useState(null);
  const [topK, setTopK] = React.useState(20);

  const loadResults = React.useCallback(() => {
    if (!tableId) return;
    rulesApi.listVerifications({ table_id: tableId, top_k: topK })
      .then((response) => setResults(response.data || []))
      .catch((err) => setError(err?.response?.data?.detail || "Could not load rule verification results."));
  }, [tableId, topK]);

  React.useEffect(() => {
    loadResults();
  }, [loadResults]);

  const summary = React.useMemo(() => {
    const passed = results.filter((item) => item.verification_status === "passed").length;
    const failed = results.filter((item) => item.verification_status === "failed").length;
    const errors = results.filter((item) => item.verification_status === "error").length;
    return { passed, failed, errors };
  }, [results]);

  return (
    <Stack spacing={3}>
      <Paper sx={{ ...panelSx, p: 3 }}>
        <Stack direction={{ xs: "column", xl: "row" }} spacing={2} justifyContent="space-between">
          <Stack spacing={1.5}>
            <Typography variant="h6" fontWeight={800}>Rule verification history</Typography>
            <Typography color="text.secondary">
              Verification reads active rules only. Each run stores one result per rule per batch so you can inspect recurring failures.
            </Typography>
            <Stack direction="row" spacing={1} flexWrap="wrap">
              <Chip size="small" color="success" label={`${summary.passed} passed`} />
              <Chip size="small" color="error" label={`${summary.failed} failed`} />
              <Chip size="small" color="warning" label={`${summary.errors} errors`} />
            </Stack>
          </Stack>

          <TextField
            select
            size="small"
            label="Top K"
            value={topK}
            onChange={(event) => setTopK(Number(event.target.value))}
            sx={{ minWidth: 110 }}
          >
            {[10, 20, 50, 100].map((value) => (
              <MenuItem key={value} value={value}>{value}</MenuItem>
            ))}
          </TextField>
        </Stack>
      </Paper>

      {error ? <Alert severity="warning" onClose={() => setError(null)}>{error}</Alert> : null}

      <Stack direction={{ xs: "column", lg: "row" }} spacing={2}>
        <Paper sx={{ ...subtlePanelSx, p: 2.5, flex: 1 }}>
          <Typography variant="overline" color="text.secondary">Latest verification rows</Typography>
          <Typography variant="h4" fontWeight={800}>{results.length}</Typography>
        </Paper>
        <Paper sx={{ ...subtlePanelSx, p: 2.5, flex: 1 }}>
          <Typography variant="overline" color="text.secondary">Failure ratio</Typography>
          <Typography variant="h4" fontWeight={800}>
            {results.length ? `${Math.round((summary.failed / results.length) * 100)}%` : "0%"}
          </Typography>
        </Paper>
        <Paper sx={{ ...subtlePanelSx, p: 2.5, flex: 1 }}>
          <Typography variant="overline" color="text.secondary">Operational state</Typography>
          <Typography variant="h4" fontWeight={800}>
            {summary.failed > 0 ? "Attention" : "Healthy"}
          </Typography>
        </Paper>
      </Stack>

      <Paper sx={{ ...panelSx, overflow: "hidden" }}>
        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Batch</TableCell>
                <TableCell>Column</TableCell>
                <TableCell>Rule type</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Actual</TableCell>
                <TableCell>Expected</TableCell>
                <TableCell>Failures</TableCell>
                <TableCell>Verified at</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {results.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={8} align="center" sx={{ py: 7, color: "text.secondary" }}>
                    No verification results yet. Active rules will appear here after the verification job runs.
                  </TableCell>
                </TableRow>
              ) : (
                results.map((result) => (
                  <TableRow key={result.id} hover>
                    <TableCell>{result.batch_date_hour}</TableCell>
                    <TableCell sx={{ fontWeight: 700 }}>{result.column_name || "--"}</TableCell>
                    <TableCell>{result.constraint_type || "--"}</TableCell>
                    <TableCell>
                      <Chip size="small" color={statusColorMap[result.verification_status] || "default"} label={result.verification_status} />
                    </TableCell>
                    <TableCell sx={{ color: datagateColors.textSecondary }}>{result.actual_value || "--"}</TableCell>
                    <TableCell sx={{ color: datagateColors.textSecondary }}>{result.expected_value || "--"}</TableCell>
                    <TableCell>{result.failure_count ?? "--"}</TableCell>
                    <TableCell>{result.verified_at?.slice?.(0, 19) || "--"}</TableCell>
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

export default RuleVerification;
