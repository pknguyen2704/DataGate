import React, { useEffect, useMemo, useState } from "react";
import {
  Alert,
  Box,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Grid,
  Paper,
  Stack,
  Typography,
} from "@mui/material";
import {
  CheckCircleOutline as HealthyIcon,
  ErrorOutline as IncidentIcon,
  WarningAmberRounded as WarningIcon,
} from "@mui/icons-material";
import { formatDistanceToNow } from "date-fns";
import { observabilityApi } from "~/apis/observability";
import { panelSx } from "~/theme";

const getSeverityColor = (severity) => {
  if (severity === "high" || severity === "critical") return "error";
  if (severity === "medium") return "warning";
  return "default";
};

const getSummaryItems = (incidents) => {
  const openIncidents = incidents.filter((incident) => incident.status === "open");
  const highSeverity = incidents.filter(
    (incident) => incident.severity === "high" || incident.severity === "critical"
  );

  return [
    { label: "Total Incidents", value: incidents.length, color: "#2563EB", icon: <IncidentIcon /> },
    { label: "Open", value: openIncidents.length, color: "#EF4444", icon: <WarningIcon /> },
    { label: "High Severity", value: highSeverity.length, color: "#F59E0B", icon: <WarningIcon /> },
  ];
};

function Incidents({ assetDetail, assetObservability, tableName: tableNameProp, initialIncidents = [] }) {
  const tableName = tableNameProp || assetDetail?.table_name;
  const hydratedIncidents = assetObservability?.incidents ?? initialIncidents;
  const [incidents, setIncidents] = useState(hydratedIncidents);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!tableName) {
      setIncidents([]);
      return;
    }

    if (hydratedIncidents.length > 0) {
      setIncidents(hydratedIncidents);
      return;
    }

    const fetchIncidents = async () => {
      try {
        setLoading(true);
        setError("");
        const response = await observabilityApi.getIncidents(tableName);
        setIncidents(response.data || []);
      } catch (fetchError) {
        console.error("Failed to fetch incidents:", fetchError);
        setError("Could not load incidents for this table.");
      } finally {
        setLoading(false);
      }
    };

    fetchIncidents();
  }, [hydratedIncidents, tableName]);

  const summaryItems = useMemo(() => getSummaryItems(incidents), [incidents]);

  if (loading) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", py: 8 }}>
        <CircularProgress size={28} />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  return (
    <Stack spacing={3}>
      <Paper sx={{ ...panelSx, p: 2.5 }}>
        <Typography variant="h6" fontWeight={700}>
          Incident Monitoring
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Review alerts and failures impacting {assetDetail?.asset_name || tableName}.
        </Typography>
      </Paper>

      <Grid container spacing={2}>
        {summaryItems.map((item) => (
          <Grid item xs={12} sm={4} key={item.label}>
            <Paper sx={{ ...panelSx, p: 2, display: "flex", alignItems: "center", gap: 2 }}>
              <Box
                sx={{
                  p: 1,
                  borderRadius: "10px",
                  bgcolor: `${item.color}15`,
                  color: item.color,
                  display: "flex",
                }}
              >
                {item.icon}
              </Box>
              <Box>
                <Typography variant="caption" color="text.secondary" fontWeight={600}>
                  {item.label}
                </Typography>
                <Typography variant="h5" fontWeight={800}>
                  {item.value}
                </Typography>
              </Box>
            </Paper>
          </Grid>
        ))}
      </Grid>

      {incidents.length === 0 ? (
        <Paper sx={{ py: 8, textAlign: "center" }}>
          <HealthyIcon sx={{ fontSize: 48, color: "success.main", mb: 1 }} />
          <Typography variant="h6" fontWeight={700}>
            No incidents
          </Typography>
          <Typography color="text.secondary">
            No active or historical incidents were found for this table.
          </Typography>
        </Paper>
      ) : (
        <Stack spacing={2}>
          {incidents.map((incident, index) => {
            const happenedAt =
              incident.detected_at ||
              incident.created_at ||
              incident.updated_at ||
              incident.event_time ||
              incident.ts;

            return (
              <Card
                key={incident.id || `${incident.incident_type}-${index}`}
                variant="outlined"
                sx={{
                  borderLeft: "4px solid",
                  borderLeftColor:
                    incident.severity === "high" || incident.severity === "critical"
                      ? "error.main"
                      : "warning.main",
                }}
              >
                <CardContent sx={{ py: 2 }}>
                  <Stack
                    direction={{ xs: "column", md: "row" }}
                    justifyContent="space-between"
                    spacing={2}
                  >
                    <Stack spacing={1}>
                      <Stack direction="row" spacing={1} alignItems="center" flexWrap="wrap">
                        <Typography variant="subtitle1" fontWeight={700}>
                          {incident.incident_type || "Incident"}
                        </Typography>
                        <Chip
                          size="small"
                          label={incident.status || "open"}
                          color={incident.status === "resolved" ? "success" : "warning"}
                        />
                        {incident.severity ? (
                          <Chip
                            size="small"
                            variant="outlined"
                            label={incident.severity}
                            color={getSeverityColor(incident.severity)}
                          />
                        ) : null}
                      </Stack>

                      <Typography variant="body2" color="text.secondary">
                        {incident.message || "No incident detail provided."}
                      </Typography>
                    </Stack>

                    <Stack spacing={0.5} alignItems={{ xs: "flex-start", md: "flex-end" }}>
                      {happenedAt ? (
                        <Typography variant="body2" fontWeight={600}>
                          {formatDistanceToNow(new Date(happenedAt), { addSuffix: true })}
                        </Typography>
                      ) : null}
                      {incident.metric_name ? (
                        <Typography variant="caption" color="text.secondary">
                          Metric: {incident.metric_name}
                        </Typography>
                      ) : null}
                    </Stack>
                  </Stack>
                </CardContent>
              </Card>
            );
          })}
        </Stack>
      )}
    </Stack>
  );
}

export default Incidents;
