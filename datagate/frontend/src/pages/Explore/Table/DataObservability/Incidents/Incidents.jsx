import React, { useState } from "react";
import {
  Box, Button, Card, CardContent, Chip, FormControl, InputLabel,
  MenuItem, Select, Stack, Typography,
} from "@mui/material";
import {
  CheckCircle as ResolveIcon,
  FilterList as FilterIcon,
} from "@mui/icons-material";
import { useDispatch } from "react-redux";
import { resolveIncident } from "~/stores/slices/exploreSlice/index";

const SEVERITY_CONFIG = {
  high: { color: "error", bg: "#ffebee" },
  medium: { color: "warning", bg: "#fff3e0" },
  low: { color: "info", bg: "#e3f2fd" },
};

const TYPE_LABELS = {
  drift: "Schema Drift",
  freshness: "Late Arrival",
  volume: "Volume Anomaly",
};

function IncidentList({ incidents = [], tableName }) {
  const dispatch = useDispatch();
  const [filterType, setFilterType] = useState("all");
  const [filterStatus, setFilterStatus] = useState("all");

  const filtered = incidents.filter((inc) => {
    if (filterType !== "all" && inc.incident_type !== filterType) return false;
    if (filterStatus !== "all" && inc.status !== filterStatus) return false;
    return true;
  });

  const openCount = incidents.filter((i) => i.status === "open").length;
  const resolvedCount = incidents.filter((i) => i.status === "resolved").length;

  const handleResolve = (incidentId) => {
    dispatch(resolveIncident({ incidentId, tableName }));
  };

  return (
    <Stack spacing={3}>
      {/* Summary */}
      <Stack direction="row" spacing={2}>
        <Card variant="outlined" sx={{ borderRadius: 2, borderColor: "#E6EBF2", flex: 1 }}>
          <CardContent sx={{ py: 1.5 }}>
            <Typography variant="caption" color="text.secondary" sx={{ textTransform: "uppercase", fontWeight: 600 }}>Open</Typography>
            <Typography sx={{ fontSize: 24, fontWeight: 700, color: openCount > 0 ? "#d32f2f" : "#2e7d32" }}>
              {openCount}
            </Typography>
          </CardContent>
        </Card>
        <Card variant="outlined" sx={{ borderRadius: 2, borderColor: "#E6EBF2", flex: 1 }}>
          <CardContent sx={{ py: 1.5 }}>
            <Typography variant="caption" color="text.secondary" sx={{ textTransform: "uppercase", fontWeight: 600 }}>Resolved</Typography>
            <Typography sx={{ fontSize: 24, fontWeight: 700, color: "#757575" }}>
              {resolvedCount}
            </Typography>
          </CardContent>
        </Card>
        <Card variant="outlined" sx={{ borderRadius: 2, borderColor: "#E6EBF2", flex: 1 }}>
          <CardContent sx={{ py: 1.5 }}>
            <Typography variant="caption" color="text.secondary" sx={{ textTransform: "uppercase", fontWeight: 600 }}>Total</Typography>
            <Typography sx={{ fontSize: 24, fontWeight: 700 }}>
              {incidents.length}
            </Typography>
          </CardContent>
        </Card>
      </Stack>

      {/* Filters */}
      <Stack direction="row" spacing={2} alignItems="center">
        <FilterIcon sx={{ color: "text.secondary", fontSize: 20 }} />
        <FormControl size="small" sx={{ minWidth: 140 }}>
          <InputLabel>Type</InputLabel>
          <Select value={filterType} label="Type" onChange={(e) => setFilterType(e.target.value)}>
            <MenuItem value="all">All Types</MenuItem>
            <MenuItem value="drift">Schema Drift</MenuItem>
            <MenuItem value="freshness">Late Arrival</MenuItem>
            <MenuItem value="volume">Volume Anomaly</MenuItem>
          </Select>
        </FormControl>
        <FormControl size="small" sx={{ minWidth: 140 }}>
          <InputLabel>Status</InputLabel>
          <Select value={filterStatus} label="Status" onChange={(e) => setFilterStatus(e.target.value)}>
            <MenuItem value="all">All Status</MenuItem>
            <MenuItem value="open">Open</MenuItem>
            <MenuItem value="resolved">Resolved</MenuItem>
          </Select>
        </FormControl>
      </Stack>

      {/* Incident Cards */}
      {filtered.length > 0 ? (
        <Stack spacing={1.5}>
          {filtered.map((inc) => {
            const sevCfg = SEVERITY_CONFIG[inc.severity] || SEVERITY_CONFIG.low;
            return (
              <Card
                key={inc.id}
                variant="outlined"
                sx={{
                  borderRadius: 2,
                  borderColor: "#E6EBF2",
                  borderLeft: `4px solid`,
                  borderLeftColor: `${sevCfg.color}.main`,
                  opacity: inc.status === "resolved" ? 0.6 : 1,
                }}
              >
                <CardContent sx={{ py: 1.5, "&:last-child": { pb: 1.5 } }}>
                  <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
                    <Box sx={{ flex: 1 }}>
                      <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 0.5 }}>
                        <Chip
                          label={TYPE_LABELS[inc.incident_type] || inc.incident_type}
                          size="small"
                          variant="outlined"
                          sx={{ fontSize: 11, fontWeight: 600 }}
                        />
                        <Chip
                          label={inc.severity?.toUpperCase()}
                          size="small"
                          color={sevCfg.color}
                          sx={{ fontSize: 10, fontWeight: 700, height: 20 }}
                        />
                        <Chip
                          label={inc.status}
                          size="small"
                          variant={inc.status === "open" ? "filled" : "outlined"}
                          color={inc.status === "open" ? "default" : "success"}
                          sx={{ fontSize: 10, height: 20 }}
                        />
                      </Stack>
                      <Typography variant="body2" sx={{ mt: 0.5 }}>
                        {inc.message}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Detected: {inc.detected_at}
                      </Typography>
                    </Box>
                    {inc.status === "open" && (
                      <Button
                        size="small"
                        startIcon={<ResolveIcon />}
                        onClick={() => handleResolve(inc.id)}
                        sx={{ textTransform: "none", fontSize: 12, ml: 2, whiteSpace: "nowrap" }}
                      >
                        Resolve
                      </Button>
                    )}
                  </Stack>
                </CardContent>
              </Card>
            );
          })}
        </Stack>
      ) : (
        <Card variant="outlined" sx={{ borderRadius: 2, borderColor: "#E6EBF2" }}>
          <CardContent sx={{ textAlign: "center", py: 6 }}>
            <Typography sx={{ fontSize: 40, mb: 1 }}>🎉</Typography>
            <Typography variant="h6" fontWeight={700} sx={{ mb: 0.5 }}>
              No Incidents Found
            </Typography>
            <Typography color="text.secondary" variant="body2">
              All data quality checks passed. No anomalies detected.
            </Typography>
          </CardContent>
        </Card>
      )}
    </Stack>
  );
}

export default IncidentList;
