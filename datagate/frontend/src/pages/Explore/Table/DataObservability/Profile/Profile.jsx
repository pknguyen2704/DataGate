import React, { useMemo } from "react";
import {
  Alert,
  Box,
  Chip,
  Divider,
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
import {
  AccountTreeOutlined as LineageIcon,
  CheckCircleOutline as HealthyIcon,
  ErrorOutline as AlertIcon,
  ScheduleOutlined as FreshnessIcon,
  StorageOutlined as TableIcon,
  StorageOutlined as VolumeIcon,
  ViewColumnOutlined as ColumnIcon,
} from "@mui/icons-material";
import { datagateColors, panelSx, subtlePanelSx } from "~/theme";

const formatValue = (value) => {
  if (value === null || value === undefined || value === "") return "--";
  if (typeof value === "number") return value.toLocaleString();
  return value;
};

const formatPercentage = (value) => {
  if (value === null || value === undefined || Number.isNaN(value)) return "--";
  return `${value.toFixed(2)}%`;
};

const toDateTime = (value) => {
  if (!value) return "--";
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return String(value);
  return parsed.toLocaleString();
};

function Profile({ assetDetail, assetObservability }) {
  const latestSnapshot = assetObservability?.snapshots?.[0] || assetDetail?.latest_snapshot;
  const incidents = assetObservability?.incidents || [];
  const volumeSeries = assetObservability?.volume || [];

  const columns = useMemo(() => {
    const schema = assetObservability?.schema || [];
    const columnStats = assetObservability?.columnStats || [];
    const statsMap = new Map(columnStats.map((item) => [item.column_name, item]));

    return schema.map((column) => {
      const stats = statsMap.get(column.column_name);
      const total = stats?.total ?? 0;
      const nulls = stats?.nulls ?? 0;
      const nullPercentage = total > 0 ? (nulls / total) * 100 : null;

      return {
        ...column,
        nullPercentage,
      };
    });
  }, [assetObservability?.columnStats, assetObservability?.schema]);

  const schemaIncidents = incidents.filter((item) => item.incident_type === "drift");
  const freshnessIncidents = incidents.filter((item) => item.incident_type === "freshness");
  const volumeIncidents = incidents.filter((item) => item.incident_type === "volume");

  const latestVolume = volumeSeries[volumeSeries.length - 1]?.records_added ?? null;
  const tableChecks = [
    {
      title: "Table exists",
      status: assetDetail?.table_name ? "healthy" : "warning",
      description: assetDetail?.table_name
        ? "The table is accessible and metadata was collected successfully."
        : "The table could not be resolved from the current metadata snapshot.",
    },
    {
      title: "Schema stability",
      status: schemaIncidents.length === 0 ? "healthy" : "warning",
      description:
        schemaIncidents.length === 0
          ? "No adverse schema changes were detected in the latest comparison."
          : `${schemaIncidents.length} schema drift incident(s) were detected.`,
    },
    {
      title: "Freshness",
      status: freshnessIncidents.length === 0 ? "healthy" : "warning",
      description:
        freshnessIncidents.length === 0
          ? "Latest update time is within the expected boundary."
          : freshnessIncidents[0]?.message || "Freshness anomalies were detected.",
    },
    {
      title: "Volume consistency",
      status: volumeIncidents.length === 0 ? "healthy" : "warning",
      description:
        volumeIncidents.length === 0
          ? "Latest volume is consistent with the expected history."
          : volumeIncidents[0]?.message || "Volume anomalies were detected.",
    },
  ];

  const gatingReady = freshnessIncidents.length === 0 && volumeIncidents.length === 0;
  const profileCards = [
    {
      label: "Table Name",
      value: assetDetail?.table_name,
      icon: <TableIcon fontSize="small" />,
    },
    {
      label: "Last Updated",
      value: toDateTime(latestSnapshot?.last_updated_time),
      icon: <FreshnessIcon fontSize="small" />,
    },
    {
      label: "Rows / Size",
      value: `${formatValue(latestSnapshot?.total_records ?? assetDetail?.row_count)} / ${formatValue(
        latestSnapshot?.total_size
      )} bytes`,
      icon: <VolumeIcon fontSize="small" />,
    },
    {
      label: "Columns",
      value: columns.length,
      icon: <ColumnIcon fontSize="small" />,
    },
  ];

  return (
    <Stack spacing={3}>
      <Alert severity="info">
        <strong>Pillar 1: Data Observability.</strong> This profile focuses on metadata collection at table and
        column level to answer existence, schema, freshness, and volume questions before deeper quality checks run.
      </Alert>

      <Grid container spacing={2}>
        {profileCards.map((card) => (
          <Grid item xs={12} sm={6} md={3} key={card.label}>
            <Paper sx={{ ...panelSx, p: 2.5, height: "100%" }}>
              <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
                {card.icon}
                <Typography variant="caption" color="text.secondary" fontWeight={700}>
                  {card.label}
                </Typography>
              </Stack>
              <Typography variant="h6" fontWeight={800}>
                {formatValue(card.value)}
              </Typography>
            </Paper>
          </Grid>
        ))}
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} lg={7}>
          <Paper sx={{ ...panelSx, p: 3, height: "100%" }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Table-Level Metadata
            </Typography>
            <Stack spacing={1.5}>
              <MetadataRow label="Asset" value={assetDetail?.asset_name} />
              <MetadataRow label="Schema" value={assetDetail?.schema_name} />
              <MetadataRow label="Table" value={assetDetail?.table_name} />
              <MetadataRow label="Latest Snapshot Time" value={toDateTime(latestSnapshot?.snapshot_time)} />
              <MetadataRow label="Last Updated Time" value={toDateTime(latestSnapshot?.last_updated_time)} />
              <MetadataRow label="Total Records" value={formatValue(latestSnapshot?.total_records ?? assetDetail?.row_count)} />
              <MetadataRow label="Total Size (bytes)" value={formatValue(latestSnapshot?.total_size)} />
              <MetadataRow label="Latest Volume Added" value={formatValue(latestVolume)} />
            </Stack>
          </Paper>
        </Grid>

        <Grid item xs={12} lg={5}>
          <Paper sx={{ ...panelSx, p: 3, height: "100%" }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Observability Checks
            </Typography>
            <Stack spacing={1.5}>
              {tableChecks.map((item) => (
                <Box
                  key={item.title}
                  sx={{ ...subtlePanelSx, p: 2 }}
                >
                  <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
                    <Typography sx={{ fontWeight: 700 }}>{item.title}</Typography>
                    <Chip
                      size="small"
                      color={item.status === "healthy" ? "success" : "warning"}
                      label={item.status === "healthy" ? "Healthy" : "Attention"}
                    />
                  </Stack>
                  <Typography variant="body2" color="text.secondary">
                    {item.description}
                  </Typography>
                </Box>
              ))}
            </Stack>
          </Paper>
        </Grid>
      </Grid>

      <Paper sx={{ ...panelSx, overflow: "hidden" }}>
        <Box sx={{ p: 3 }}>
          <Typography variant="h6" sx={{ mb: 0.5 }}>
            Column-Level Metadata
          </Typography>
          <Typography color="text.secondary">
            Metadata is collected non-intrusively from system views and includes table name, column name, data type,
            and null-rate statistics when available.
          </Typography>
        </Box>
        <Divider />
        <TableContainer>
          <Table size="small">
            <TableHead sx={{ bgcolor: datagateColors.tableHeadBackground }}>
              <TableRow>
                <TableCell>Table</TableCell>
                <TableCell>Column</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Null %</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {columns.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={4} align="center" sx={{ py: 6 }}>
                    <Typography color="text.secondary">No column metadata is available yet.</Typography>
                  </TableCell>
                </TableRow>
              ) : (
                columns.map((column, index) => (
                  <TableRow key={`${column.column_name}-${index}`} hover>
                    <TableCell>{assetDetail?.table_name || "--"}</TableCell>
                    <TableCell sx={{ fontWeight: 600 }}>{column.column_name}</TableCell>
                    <TableCell>
                      <Chip size="small" variant="outlined" label={column.data_type || "--"} />
                    </TableCell>
                    <TableCell>{formatPercentage(column.nullPercentage)}</TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      <Grid container spacing={3}>
        <Grid item xs={12} lg={6}>
          <Paper sx={{ ...panelSx, p: 3, height: "100%" }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Predictive Alerts
            </Typography>
            <Stack spacing={1.5}>
              <StatusRow
                icon={<FreshnessIcon color={freshnessIncidents.length === 0 ? "success" : "warning"} />}
                title="Freshness forecast"
                text={
                  freshnessIncidents.length === 0
                    ? "Historical update timings indicate the latest refresh is still within its predicted boundary."
                    : freshnessIncidents[0]?.message || "A freshness delay was detected against the expected update window."
                }
              />
              <StatusRow
                icon={<VolumeIcon color={volumeIncidents.length === 0 ? "success" : "warning"} />}
                title="Volume forecast"
                text={
                  volumeIncidents.length === 0
                    ? "Latest volume remains consistent with the expected historical baseline."
                    : volumeIncidents[0]?.message || "Latest volume is unexpectedly low compared with historical behavior."
                }
              />
            </Stack>
          </Paper>
        </Grid>

        <Grid item xs={12} lg={6}>
          <Paper sx={{ ...panelSx, p: 3, height: "100%" }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Lineage & Job Monitoring
            </Typography>
            <Stack spacing={1.5}>
              <StatusRow
                icon={<LineageIcon color="primary" />}
                title="Lineage readiness"
                text="Data lineage can be used to trace upstream failures when freshness or schema incidents occur. Connect the Lineage module for full source-to-target tracing."
              />
              <StatusRow
                icon={<AlertIcon color={incidents.length === 0 ? "success" : "warning"} />}
                title="Job monitoring signal"
                text={
                  incidents.length === 0
                    ? "No active ingestion or metadata-related incidents are currently affecting this table."
                    : `${incidents.length} active incident(s) provide operational signals for this table's data flow.`
                }
              />
            </Stack>
          </Paper>
        </Grid>
      </Grid>

      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" sx={{ mb: 2 }}>
          Gating Status
        </Typography>
        <Stack direction={{ xs: "column", md: "row" }} spacing={2} alignItems={{ md: "center" }} justifyContent="space-between">
          <Box>
            <Typography sx={{ fontWeight: 700, mb: 0.5 }}>
              {gatingReady ? "Ready for deeper quality checks" : "Hold deeper quality checks"}
            </Typography>
            <Typography color="text.secondary">
              Freshness and volume checks are evaluated first to prevent false positives caused by incomplete or delayed
              loads before downstream quality rules and ML anomaly detection execute.
            </Typography>
          </Box>
          <Chip
            icon={gatingReady ? <HealthyIcon /> : <AlertIcon />}
            color={gatingReady ? "success" : "warning"}
            label={gatingReady ? "Gate Open" : "Gate Blocked"}
          />
        </Stack>
      </Paper>
    </Stack>
  );
}

function MetadataRow({ label, value }) {
  return (
    <Stack direction="row" justifyContent="space-between" spacing={2}>
      <Typography color="text.secondary">{label}</Typography>
      <Typography sx={{ fontWeight: 600, textAlign: "right" }}>{value || "--"}</Typography>
    </Stack>
  );
}

function StatusRow({ icon, title, text }) {
  return (
    <Box sx={{ p: 2, border: "1px solid #E5EAF2", borderRadius: 2 }}>
      <Stack direction="row" spacing={1.25} alignItems="center" sx={{ mb: 1 }}>
        {icon}
        <Typography sx={{ fontWeight: 700 }}>{title}</Typography>
      </Stack>
      <Typography variant="body2" color="text.secondary">
        {text}
      </Typography>
    </Box>
  );
}

export default Profile;
