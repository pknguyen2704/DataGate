import React from "react";
import {
  Box, Card, CardContent, Chip, Divider, Stack, Typography,
} from "@mui/material";
import {
  Add as AddIcon,
  Remove as RemoveIcon,
  SwapHoriz as ChangeIcon,
} from "@mui/icons-material";

const CHANGE_CONFIG = {
  added: { color: "success", icon: <AddIcon sx={{ fontSize: 14 }} />, label: "Added" },
  removed: { color: "error", icon: <RemoveIcon sx={{ fontSize: 14 }} />, label: "Removed" },
  type_changed: { color: "warning", icon: <ChangeIcon sx={{ fontSize: 14 }} />, label: "Type Changed" },
};

function SchemaHistory({ schemaHistory, tableName }) {
  if (!schemaHistory) {
    return (
      <Box sx={{ display: "flex", alignItems: "center", justifyContent: "center", py: 10, bgcolor: "#fafafa", borderRadius: 2 }}>
        <Typography color="text.secondary" variant="body2">
          Loading schema history...
        </Typography>
      </Box>
    );
  }

  const { changes = [], total_snapshots = 0 } = schemaHistory;

  return (
    <Stack spacing={3}>
      {/* Summary */}
      <Card variant="outlined" sx={{ borderRadius: 2, borderColor: "#E6EBF2" }}>
        <CardContent>
          <Stack direction="row" spacing={3} alignItems="center">
            <Box>
              <Typography variant="caption" color="text.secondary" sx={{ textTransform: "uppercase", fontWeight: 600, letterSpacing: 0.5 }}>
                Total Schema Snapshots
              </Typography>
              <Typography sx={{ fontSize: 28, fontWeight: 700, mt: 0.5 }}>
                {total_snapshots}
              </Typography>
            </Box>
            <Divider orientation="vertical" flexItem />
            <Box>
              <Typography variant="caption" color="text.secondary" sx={{ textTransform: "uppercase", fontWeight: 600, letterSpacing: 0.5 }}>
                Schema Changes Detected
              </Typography>
              <Typography sx={{ fontSize: 28, fontWeight: 700, mt: 0.5, color: changes.length > 0 ? "#f57c00" : "#2e7d32" }}>
                {changes.length}
              </Typography>
            </Box>
          </Stack>
        </CardContent>
      </Card>

      {/* Changes Timeline */}
      {changes.length > 0 ? (
        <Card variant="outlined" sx={{ borderRadius: 2, borderColor: "#E6EBF2" }}>
          <CardContent>
            <Typography variant="subtitle1" fontWeight={700} sx={{ mb: 2 }}>
              Schema Change History
            </Typography>
            {changes.map((change, idx) => (
              <Box key={idx} sx={{ mb: 3, pb: 3, borderBottom: idx < changes.length - 1 ? "1px solid #f0f0f0" : "none" }}>
                <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1.5 }}>
                  <Chip label={change.snapshot_time} size="small" variant="outlined" sx={{ fontSize: 11, fontWeight: 600 }} />
                  <Typography variant="caption" color="text.secondary">
                    compared to {change.compared_to}
                  </Typography>
                </Stack>
                <Stack spacing={1}>
                  {change.changes.map((diff, i) => {
                    const cfg = CHANGE_CONFIG[diff.change] || CHANGE_CONFIG.type_changed;
                    return (
                      <Stack key={i} direction="row" spacing={1} alignItems="center" sx={{ px: 2, py: 0.75, borderRadius: 1, bgcolor: "#f9f9f9" }}>
                        <Chip
                          icon={cfg.icon}
                          label={cfg.label}
                          size="small"
                          color={cfg.color}
                          variant="outlined"
                          sx={{ fontSize: 11, fontWeight: 600 }}
                        />
                        <Typography variant="body2" fontWeight={600} sx={{ fontFamily: "monospace" }}>
                          {diff.column}
                        </Typography>
                        {diff.change === "type_changed" && (
                          <Typography variant="body2" color="text.secondary">
                            <code>{diff.old_type}</code> → <code>{diff.new_type}</code>
                          </Typography>
                        )}
                        {diff.change === "added" && (
                          <Typography variant="body2" color="text.secondary">
                            type: <code>{diff.new_type}</code>
                          </Typography>
                        )}
                        {diff.change === "removed" && (
                          <Typography variant="body2" color="text.secondary">
                            was: <code>{diff.old_type}</code>
                          </Typography>
                        )}
                      </Stack>
                    );
                  })}
                </Stack>
              </Box>
            ))}
          </CardContent>
        </Card>
      ) : (
        <Card variant="outlined" sx={{ borderRadius: 2, borderColor: "#E6EBF2" }}>
          <CardContent sx={{ textAlign: "center", py: 6 }}>
            <Typography sx={{ fontSize: 40, mb: 1 }}>✅</Typography>
            <Typography variant="h6" fontWeight={700} sx={{ mb: 0.5 }}>
              No Schema Changes Detected
            </Typography>
            <Typography color="text.secondary" variant="body2">
              The schema has been stable across all recorded snapshots.
            </Typography>
          </CardContent>
        </Card>
      )}
    </Stack>
  );
}

export default SchemaHistory;
