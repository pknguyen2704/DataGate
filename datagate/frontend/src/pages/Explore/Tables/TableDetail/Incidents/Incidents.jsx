import React, { useEffect } from "react";
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Tooltip,
} from "@mui/material";
import {
  CheckCircleOutline as ResolveIcon,
  ErrorOutline as ErrorIcon,
  Timeline as VolumeIcon,
  Schema as SchemaIcon,
} from "@mui/icons-material";
import { useDispatch, useSelector } from "react-redux";
import { fetchIncidents, resolveIncident } from "~/stores/slices/exploreSlice/index";
import { toast } from "react-toastify";
import { format } from "date-fns";

const getIncidentIcon = (type) => {
  switch (type) {
    case "volume":
      return <VolumeIcon color="primary" sx={{ fontSize: 20 }} />;
    case "drift":
      return <SchemaIcon color="warning" sx={{ fontSize: 20 }} />;
    default:
      return <ErrorIcon color="error" sx={{ fontSize: 20 }} />;
  }
};

const getSeverityColor = (severity) => {
  switch (severity) {
    case "high":
      return "error";
    case "medium":
      return "warning";
    default:
      return "info";
  }
};

function Incidents({ assetDetail }) {
  const dispatch = useDispatch();
  const tableName = assetDetail?.table_name || assetDetail?.asset_name;
  const schemaName = assetDetail?.schema_name || "public";
  const key = `${schemaName}.${tableName}`;

  const { incidentsByTable } = useSelector((state) => state.explore.observability);
  const incidents = incidentsByTable[key] || [];

  useEffect(() => {
    if (tableName) {
      dispatch(fetchIncidents({ tableName, schemaName }));
    }
  }, [dispatch, tableName, schemaName]);

  const handleResolve = async (incidentId) => {
    try {
      await dispatch(resolveIncident({ incidentId, key })).unwrap();
      toast.success("Incident resolved successfully.");
    } catch (e) {
      toast.error("Error resolving incident.");
    }
  };

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h6" sx={{ mb: 2, fontWeight: 700, display: "flex", alignItems: "center", gap: 1 }}>
        <ErrorIcon color="error" /> Detected Incidents
      </Typography>

      <TableContainer component={Paper} elevation={0} sx={{ border: "1px solid", borderColor: "divider", borderRadius: 2 }}>
        <Table size="small">
          <TableHead sx={{ bgcolor: "action.hover" }}>
            <TableRow>
              <TableCell sx={{ fontWeight: 700, fontSize: 13 }}>Type</TableCell>
              <TableCell sx={{ fontWeight: 700, fontSize: 13 }}>Severity</TableCell>
              <TableCell sx={{ fontWeight: 700, fontSize: 13 }}>Details</TableCell>
              <TableCell sx={{ fontWeight: 700, fontSize: 13 }}>Detected At</TableCell>
              <TableCell sx={{ fontWeight: 700, fontSize: 13 }}>Status</TableCell>
              <TableCell align="right" sx={{ fontWeight: 700, fontSize: 13 }}>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {incidents.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} align="center" sx={{ py: 6, color: "text.secondary" }}>
                   No incidents found for this table.
                </TableCell>
              </TableRow>
            ) : (
              incidents.map((incident) => (
                <TableRow key={incident.id} hover>
                  <TableCell>
                    <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                      {getIncidentIcon(incident.incident_type)}
                      <Typography variant="body2" sx={{ fontWeight: 500, textTransform: "capitalize", fontSize: 13 }}>
                        {incident.incident_type}
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={incident.severity}
                      size="small"
                      color={getSeverityColor(incident.severity)}
                      sx={{ fontWeight: 700, fontSize: 10, textTransform: "uppercase", height: 20 }}
                    />
                  </TableCell>
                  <TableCell sx={{ maxWidth: 300 }}>
                    <Typography variant="body2" sx={{ whiteSpace: "normal", fontSize: 13 }}>
                      {incident.message}
                    </Typography>
                  </TableCell>
                  <TableCell sx={{ fontSize: 13 }}>
                    {incident.detected_at ? format(new Date(incident.detected_at), "MMM d, yyyy HH:mm") : "—"}
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={incident.status}
                      size="small"
                      variant={incident.status === "open" ? "filled" : "outlined"}
                      color={incident.status === "open" ? "error" : "success"}
                      sx={{ height: 20, fontSize: 11 }}
                    />
                  </TableCell>
                  <TableCell align="right">
                    {incident.status === "open" && (
                      <Tooltip title="Resolve">
                        <IconButton size="small" color="success" onClick={() => handleResolve(incident.id)}>
                          <ResolveIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    )}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}

export default Incidents;