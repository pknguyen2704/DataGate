import { Box, Button, Chip, CircularProgress, Paper, Stack, Typography } from "@mui/material";
import { datagateColors } from "~/theme";

const cardSx = {
  borderRadius: 2,
  border: "1px solid",
  borderColor: "divider",
  bgcolor: "white",
};

const statusColors = {
  error: datagateColors.error,
  warning: datagateColors.warning,
  success: datagateColors.success,
  pending: "#6366F1",
  default: "#64748B",
};

export const Panel = ({ title, subtitle, action, children, sx }) => (
  <Paper sx={{ ...cardSx, p: 3, ...sx }}>
    {(title || subtitle || action) && (
      <Stack direction="row" justifyContent="space-between" alignItems="flex-start" gap={2} sx={{ mb: 3 }}>
        <Box>
          {title && (
            <Typography variant="h6" sx={{ fontWeight: 800 }}>
              {title}
            </Typography>
          )}
          {subtitle && (
            <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5, fontWeight: 500 }}>
              {subtitle}
            </Typography>
          )}
        </Box>
        {action}
      </Stack>
    )}
    {children}
  </Paper>
);

export const Stat = ({ label, value, tone = "blue", subtitle }) => {
  const color = datagateColors.statTones[tone] || datagateColors.statTones.blue;

  return (
    <Paper
      variant="outlined"
      sx={{
        ...cardSx,
        height: "100%",
        p: 2,
        bgcolor: color.background,
        borderColor: color.border,
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        position: "relative",
        overflow: "hidden",
        transition: "all 0.2s ease",
        "&:hover": {
          transform: "translateY(-3px)",
          boxShadow: "0 12px 20px rgba(15, 23, 42, 0.08)",
          borderColor: color.accent,
        },
      }}
    >
      <Box sx={{ position: "absolute", inset: "0 auto 0 0", width: 4, bgcolor: color.accent }} />
      <Typography variant="overline" sx={{ color: "text.secondary", fontSize: "0.65rem" }}>
        {label}
      </Typography>
      <Typography variant="h4" sx={{ mt: 0.5, color: color.accent, fontWeight: 900 }}>
        {value ?? "-"}
      </Typography>
      {subtitle && (
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1, fontWeight: 500 }}>
          {subtitle}
        </Typography>
      )}
    </Paper>
  );
};

export const StatusChip = ({ value }) => {
  const normalized = String(value || "unknown").toLowerCase();
  const isError = ["fail", "failure", "critical", "inactive", "no"].some((text) => normalized.includes(text));
  const isWarning = ["warning", "warn"].some((text) => normalized.includes(text));
  const isSuccess = ["pass", "success", "active", "yes"].some((text) => normalized.includes(text));
  const isPending = normalized.includes("pending");
  const isDefault = normalized.includes("unknown") || normalized.includes("manual");

  const label = isError ? "FAIL" : isSuccess ? "PASS" : normalized.toUpperCase();
  const bgcolor = isError
    ? statusColors.error
    : isWarning
      ? statusColors.warning
      : isSuccess
        ? statusColors.success
        : isPending
          ? statusColors.pending
          : isDefault
            ? statusColors.default
            : statusColors.success;

  return (
    <Chip
      size="small"
      label={label}
      sx={{
        bgcolor,
        color: "white",
        fontWeight: 700,
        fontSize: "0.72rem",
        borderRadius: "6px",
        height: 22,
        textTransform: "uppercase",
      }}
    />
  );
};

export const StateBox = ({ loading, error, empty, children }) => {
  if (loading) {
    return (
      <Box sx={{ py: 10, textAlign: "center", width: "100%" }}>
        <CircularProgress size={32} />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 4, textAlign: "center" }}>
        <Typography color="error" fontWeight="bold">
          {String(error)}
        </Typography>
      </Box>
    );
  }

  if (empty) {
    return (
      <Box sx={{ p: 4, textAlign: "center" }}>
        <Typography color="text.secondary">No data available.</Typography>
      </Box>
    );
  }

  return children;
};

export const TabContainer = ({ children }) => (
  <Paper
    variant="outlined"
    sx={{
      p: 0.5,
      mb: 3,
      borderRadius: "12px",
      display: "inline-flex",
      gap: 1,
      bgcolor: datagateColors.cardBackgroundMuted,
      overflow: "hidden",
    }}
  >
    {children}
  </Paper>
);

export const TabButton = ({ active, label, onClick, icon }) => (
  <Button
    variant={active ? "contained" : "text"}
    onClick={onClick}
    startIcon={icon}
    sx={{
      borderRadius: "10px",
      px: 3,
      py: 1.2,
      fontWeight: 700,
      color: active ? "white" : "text.secondary",
      bgcolor: active ? "primary.main" : "transparent",
      "&:hover": {
        bgcolor: active ? "primary.dark" : "rgba(15, 23, 42, 0.04)",
      },
    }}
  >
    {label}
  </Button>
);

