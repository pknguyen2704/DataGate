import React from 'react';
import {
  Box, Typography, Grid, Paper, Skeleton, Chip
} from '@mui/material';
import {
  TableChartOutlined,
  NotificationsNoneOutlined,
  CheckCircleOutlined,
  WarningAmberOutlined,
  ErrorOutlineOutlined,
  HelpOutlineOutlined,
  WorkHistoryOutlined,
} from '@mui/icons-material';
import { useDispatch, useSelector } from 'react-redux';
import { dashboardApi } from '~/apis/api';
import { pageShellSx, panelSx } from '~/theme';

// ── KPI Card ────────────────────────────────────────────────────────────────

const KpiCard = ({ label, value, icon, color = 'primary.main', loading }) => (
  <Paper
    elevation={0}
    sx={{
      ...panelSx,
      p: 3,
      display: 'flex',
      alignItems: 'center',
      gap: 2.5,
      transition: 'box-shadow 0.2s',
      '&:hover': { boxShadow: '0 4px 20px rgba(15,23,42,0.08)' },
    }}
  >
    <Box
      sx={{
        width: 52,
        height: 52,
        borderRadius: '12px',
        bgcolor: `${color}15`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexShrink: 0,
      }}
    >
      {React.cloneElement(icon, { sx: { color, fontSize: 26 } })}
    </Box>
    <Box>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 0.25 }}>
        {label}
      </Typography>
      {loading ? (
        <Skeleton width={60} height={36} />
      ) : (
        <Typography variant="h5" fontWeight={700} sx={{ lineHeight: 1 }}>
          {value ?? '—'}
        </Typography>
      )}
    </Box>
  </Paper>
);

// ── Health Bar ───────────────────────────────────────────────────────────────

const HealthBar = ({ health, loading }) => {
  if (loading) return <Skeleton height={120} />;

  const total = Object.values(health).reduce((a, b) => a + b, 0) || 1;
  const segments = [
    { key: 'healthy', label: 'Healthy', color: '#16A34A' },
    { key: 'warning', label: 'Warning', color: '#F59E0B' },
    { key: 'failed', label: 'Failed', color: '#EF4444' },
    { key: 'unknown', label: 'No data', color: '#94A3B8' },
  ];

  return (
    <Paper elevation={0} sx={{ ...panelSx, p: 3 }}>
      <Typography variant="subtitle1" fontWeight={700} mb={2}>
        Table Health Distribution
      </Typography>
      {/* Stacked bar */}
      <Box sx={{ display: 'flex', height: 12, borderRadius: 999, overflow: 'hidden', mb: 2 }}>
        {segments.map(({ key, color }) =>
          health[key] > 0 ? (
            <Box
              key={key}
              sx={{
                width: `${(health[key] / total) * 100}%`,
                bgcolor: color,
                transition: 'width 0.5s ease',
              }}
            />
          ) : null
        )}
      </Box>
      {/* Legend */}
      <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
        {segments.map(({ key, label, color }) => (
          <Box key={key} sx={{ display: 'flex', alignItems: 'center', gap: 0.75 }}>
            <Box sx={{ width: 10, height: 10, borderRadius: '50%', bgcolor: color }} />
            <Typography variant="caption" color="text.secondary">
              {label}: <strong>{health[key] || 0}</strong>
            </Typography>
          </Box>
        ))}
      </Box>
    </Paper>
  );
};

// ── Home Page ────────────────────────────────────────────────────────────────

export default function Home() {
  const [summary, setSummary] = React.useState(null);
  const [loading, setLoading] = React.useState(true);
  const { user } = useSelector((s) => s.auth);

  React.useEffect(() => {
    dashboardApi.getSummary()
      .then((res) => setSummary(res.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const health = summary?.table_health || {};

  return (
    <Box sx={pageShellSx}>
      {/* Header */}
      <Box mb={4}>
        <Typography variant="h4" fontWeight={800} mb={0.5}>
          Welcome back{user?.full_name ? `, ${user.full_name.split(' ')[0]}` : ''} 👋
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Data Quality Management Platform — system overview
        </Typography>
      </Box>

      {/* KPI Grid */}
      <Grid container spacing={2.5} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <KpiCard
            label="Monitored Tables"
            value={summary?.total_monitored_tables}
            icon={<TableChartOutlined />}
            color="primary.main"
            loading={loading}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KpiCard
            label="Open Alerts"
            value={summary?.open_alerts}
            icon={<NotificationsNoneOutlined />}
            color="#F59E0B"
            loading={loading}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KpiCard
            label="Critical Alerts"
            value={summary?.critical_alerts}
            icon={<ErrorOutlineOutlined />}
            color="#EF4444"
            loading={loading}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KpiCard
            label="Recent Failed Jobs"
            value={summary?.recent_failed_jobs}
            icon={<WorkHistoryOutlined />}
            color="#8B5CF6"
            loading={loading}
          />
        </Grid>
      </Grid>

      {/* Health + Status */}
      <Grid container spacing={2.5}>
        <Grid item xs={12} md={6}>
          <HealthBar health={health} loading={loading} />
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper elevation={0} sx={{ ...panelSx, p: 3 }}>
            <Typography variant="subtitle1" fontWeight={700} mb={2}>
              Table Status Breakdown
            </Typography>
            {loading ? (
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                {[1, 2, 3, 4].map((k) => <Skeleton key={k} height={36} />)}
              </Box>
            ) : (
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                {[
                  { key: 'healthy', label: 'Healthy', color: 'success', icon: <CheckCircleOutlined fontSize="small" /> },
                  { key: 'warning', label: 'Warning', color: 'warning', icon: <WarningAmberOutlined fontSize="small" /> },
                  { key: 'failed', label: 'Failed', color: 'error', icon: <ErrorOutlineOutlined fontSize="small" /> },
                  { key: 'unknown', label: 'No data collected', color: 'default', icon: <HelpOutlineOutlined fontSize="small" /> },
                ].map(({ key, label, color, icon }) => (
                  <Box
                    key={key}
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      p: 1.5,
                      borderRadius: 1,
                      bgcolor: 'background.default',
                      border: '1px solid',
                      borderColor: 'divider',
                    }}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      {icon}
                      <Typography variant="body2" fontWeight={500}>{label}</Typography>
                    </Box>
                    <Chip label={health[key] || 0} color={color} size="small" />
                  </Box>
                ))}
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}