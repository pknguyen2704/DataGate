import { 
  Box, Chip, CircularProgress, Paper, Stack, Typography, Button, IconButton as MuiIconButton 
} from "@mui/material";
import { datagateColors, panelSx } from "~/theme";

const GLOBAL_RADIUS = 2; // 16px

export const Page = ({ title, subtitle, actions, children }) => (
  <Box sx={{ 
    p: { xs: 2, md: 3 }, 
    bgcolor: "background.default", 
    flexGrow: 1,
    width: '100%',
    height: '100%',
    overflow: "hidden", 
    display: "flex", 
    flexDirection: "column" 
  }}>
    <Stack spacing={3} sx={{ height: '100%', width: '100%' }}>
      <Paper variant="outlined" sx={{ 
        p: 2.5, 
        borderRadius: GLOBAL_RADIUS, 
        display: 'flex', 
        flexDirection: { xs: "column", md: "row" }, 
        justifyContent: "space-between", 
        alignItems: { md: "center" }, 
        gap: 2, 
        flexShrink: 0,
        width: '100%',
        bgcolor: 'white',
        border: '1px solid',
        borderColor: 'divider',
        boxShadow: '0 2px 10px rgba(0,0,0,0.02)'
      }}>
        <Box>
          <Typography variant="h5" sx={{ color: datagateColors.shell, fontWeight: 800 }}>{title}</Typography>
          {subtitle && <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5, fontWeight: 500 }}>{subtitle}</Typography>}
        </Box>
        {actions}
      </Paper>
      <Box sx={{ flexGrow: 1, overflow: 'auto', width: '100%' }}>
        {children}
      </Box>
    </Stack>
  </Box>
);

export const TabContainer = ({ children }) => (
  <Paper 
    variant="outlined" 
    sx={{ 
      p: 0.5, 
      mb: 3, 
      borderRadius: '12px', 
      display: 'inline-flex', 
      gap: 1,
      bgcolor: '#F8FAFC',
      border: '1px solid',
      borderColor: 'divider',
      overflow: 'hidden'
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
      borderRadius: '10px',
      px: 3,
      py: 1.2,
      fontWeight: 'bold',
      fontSize: '0.875rem',
      color: active ? 'white' : 'text.secondary',
      bgcolor: active ? 'primary.main' : 'transparent',
      '&:hover': {
        bgcolor: active ? 'primary.dark' : 'rgba(0,0,0,0.04)',
      },
      boxShadow: active ? '0 4px 12px rgba(37, 99, 235, 0.2)' : 'none',
      textTransform: 'none',
      transition: 'all 0.2s'
    }}
  >
    {label}
  </Button>
);

export const Panel = ({ title, subtitle, action, children, sx }) => (
  <Paper sx={{ 
    ...panelSx, 
    p: 3, 
    borderRadius: GLOBAL_RADIUS, 
    border: '1px solid',
    borderColor: 'divider',
    bgcolor: 'white',
    ...sx 
  }}>
    {(title || subtitle || action) && (
      <Stack direction="row" justifyContent="space-between" alignItems="flex-start" gap={2} sx={{ mb: 3 }}>
        <Box>
          {title && <Typography variant="h6" sx={{ fontWeight: 800, color: "text.primary", letterSpacing: "-0.01em" }}>{title}</Typography>}
          {subtitle && <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5, fontWeight: 500 }}>{subtitle}</Typography>}
        </Box>
        {action}
      </Stack>
    )}
    {children}
  </Paper>
);

export const Stat = ({ label, value, tone = "blue", subtitle }) => {
  const colors = {
    blue: ["#EFF6FF", "#2563EB"],
    green: ["#ECFDF5", "#10B981"],
    amber: ["#FFFBEB", "#F59E0B"],
    red: ["#FEF2F2", "#EF4444"],
  };
  const [bgcolor, color] = colors[tone] || colors.blue;
  return (
    <Paper 
      variant="outlined"
      sx={{ 
        height: "100%", 
        borderRadius: GLOBAL_RADIUS,
        transition: "all 0.3s ease", 
        "&:hover": { 
          transform: "translateY(-4px)",
          boxShadow: "0 12px 20px rgba(0,0,0,0.05)",
          borderColor: color
        },
        p: 2,
        bgcolor: 'white',
        border: '1px solid',
        borderColor: 'divider',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        position: 'relative',
        overflow: 'hidden'
      }}
    >
      <Box sx={{ position: 'absolute', top: 0, left: 0, width: 4, height: '100%', bgcolor: color }} />
      <Typography variant="overline" sx={{ color: "text.secondary", fontWeight: 700, letterSpacing: 1.2, opacity: 0.8, fontSize: '0.65rem' }}>{label}</Typography>
      <Typography variant="h4" sx={{ mt: 0.5, color, fontWeight: 900 }}>{value ?? "—"}</Typography>
      {subtitle && <Typography variant="body2" color="text.secondary" sx={{ mt: 1, fontWeight: 500 }}>{subtitle}</Typography>}
    </Paper>
  );
};

export const StatusChip = ({ value }) => {
  const normalized = String(value || "unknown").toLowerCase();
  const isError = normalized.includes("fail") || normalized.includes("failure") || normalized.includes("critical") || normalized.includes("inactive") || normalized.includes("no");
  const isWarning = normalized.includes("warning") || normalized.includes("warn");
  const isSuccess = normalized.includes("pass") || normalized.includes("success") || normalized.includes("active") || normalized.includes("yes");
  const isPending = normalized.includes("pending");
  const isDefault = normalized.includes("unknown") || normalized.includes("manual");
  
  const labelText = isError ? "FAIL" : isWarning ? (normalized.toUpperCase()) : isSuccess ? "PASS" : normalized.toUpperCase();
  const bgcolor = isError ? "#EF4444" : isWarning ? "#F59E0B" : isSuccess ? "#10B981" : isPending ? "#6366F1" : isDefault ? "#64748B" : "#10B981";
  const color = "#FFFFFF";

  return (
    <Chip 
      size="small" 
      label={labelText} 
      sx={{ 
        bgcolor, 
        color, 
        fontWeight: 700, 
        fontSize: "0.72rem",
        borderRadius: "6px",
        height: 22,
        px: 0.5,
        textTransform: "uppercase",
        border: 'none',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
      }} 
    />
  );
};

export const StateBox = ({ loading, error, empty, children }) => {
  if (loading) return <Box sx={{ py: 10, textAlign: "center", width: '100%' }}><CircularProgress size={32} /></Box>;
  if (error) return <Box sx={{ p: 4, textAlign: 'center' }}><Typography color="error" fontWeight="bold">{String(error)}</Typography></Box>;
  if (empty) return <Box sx={{ p: 4, textAlign: 'center' }}><Typography color="text.secondary">No data available.</Typography></Box>;
  return children;
};
