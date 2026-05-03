import React from "react";
import {
  Alert,
  Box,
  Chip,
  Paper,
  Stack,
  Typography,
} from "@mui/material";
import {
  DashboardOutlined as DashboardIcon,
} from "@mui/icons-material";
import { panelSx } from "~/theme";

const DEFAULT_GRAFANA_PATH = "/d/datagate-overview/datagate-overview?orgId=1";

const getGrafanaBaseUrl = () => {
  const configured = import.meta.env.VITE_GRAFANA_TABLE_DASHBOARD_URL;
  if (configured) return configured;
  if (typeof window === "undefined") return null;
  const { protocol, hostname } = window.location;
  return `${protocol}//${hostname}:3000${DEFAULT_GRAFANA_PATH}`;
};

function Overview({ assetDetail, tableId }) {
  const grafanaUrl = React.useMemo(() => {
    const baseUrl = getGrafanaBaseUrl();
    if (!baseUrl || !tableId) return null;

    const params = new URLSearchParams();
    params.set("var-table_id", tableId);
    params.set("theme", "dark");
    return `${baseUrl}${baseUrl.includes("?") ? "&" : "?"}${params.toString()}`;
  }, [tableId]);

  return (
    <Paper sx={{ ...panelSx, overflow: "hidden" }}>
      <Stack
        direction={{ xs: "column", lg: "row" }}
        spacing={2}
        justifyContent="space-between"
        alignItems={{ xs: "flex-start", lg: "center" }}
        sx={{ px: 3, py: 2.5, borderBottom: "1px solid", borderColor: "divider" }}
      >
        <Stack spacing={0.75}>
          <Stack direction="row" spacing={1} alignItems="center">
            <DashboardIcon color="primary" />
            <Typography variant="h6" fontWeight={800}>
              Grafana overview
            </Typography>
          </Stack>
          <Typography color="text.secondary">
            Metadata charts and analyzer results are rendered directly from Grafana. Use Grafana's own filters and time controls in the embedded dashboard.
          </Typography>
          <Chip
            size="small"
            variant="outlined"
            label={assetDetail?.full_name || [assetDetail?.catalog_name, assetDetail?.schema_name, assetDetail?.table_name].filter(Boolean).join(".")}
            sx={{ alignSelf: "flex-start" }}
          />
        </Stack>
      </Stack>

      <Box sx={{ p: 3 }}>
        {grafanaUrl ? (
          <Box
            component="iframe"
            title="Grafana DataGate Overview"
            src={grafanaUrl}
            sx={{
              width: "100%",
              minHeight: "1200px",
              border: 0,
              borderRadius: "12px",
              backgroundColor: "#081326",
            }}
          />
        ) : (
          <Alert severity="info">
            Grafana dashboard URL is not available. Set <code>VITE_GRAFANA_TABLE_DASHBOARD_URL</code> or run Grafana on port 3000.
          </Alert>
        )}
      </Box>
    </Paper>
  );
}

export default Overview;
