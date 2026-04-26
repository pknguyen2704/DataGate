import React from 'react';
import {
  Box, Typography, Paper, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Chip, IconButton, Tooltip, Stack,
  Select, FormControl, InputLabel, MenuItem, Skeleton, Button,
} from '@mui/material';
import { RefreshOutlined, CheckOutlined, ArchiveOutlined } from '@mui/icons-material';
import { alertsApi } from '~/apis/api';
import { pageShellSx, panelSx } from '~/theme';

const SEVERITY_COLORS = { low: 'default', medium: 'warning', high: 'error', critical: 'error' };
const STATUS_COLORS = { open: 'error', acknowledged: 'warning', resolved: 'success', ignored: 'default' };

export default function Alerts() {
  const [alerts, setAlerts] = React.useState([]);
  const [loading, setLoading] = React.useState(true);
  const [statusFilter, setStatusFilter] = React.useState('open');
  const [severityFilter, setSeverityFilter] = React.useState('');

  const load = React.useCallback(() => {
    setLoading(true);
    alertsApi.list({ status: statusFilter || undefined, severity: severityFilter || undefined })
      .then((r) => setAlerts(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [statusFilter, severityFilter]);

  React.useEffect(() => { load(); }, [load]);

  const updateStatus = async (id, status) => {
    await alertsApi.updateStatus(id, status);
    load();
  };

  return (
    <Box sx={pageShellSx}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 3 }}>
        <Box>
          <Typography variant="h4" fontWeight={800} mb={0.5}>Alerts</Typography>
          <Typography variant="body1" color="text.secondary">
            {alerts.length} alert{alerts.length !== 1 ? 's' : ''} matching filter
          </Typography>
        </Box>
        <Tooltip title="Refresh">
          <IconButton onClick={load} size="small" sx={{ border: '1px solid', borderColor: 'divider' }}>
            <RefreshOutlined fontSize="small" />
          </IconButton>
        </Tooltip>
      </Box>

      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        <FormControl size="small" sx={{ minWidth: 140 }}>
          <InputLabel>Status</InputLabel>
          <Select value={statusFilter} label="Status" onChange={(e) => setStatusFilter(e.target.value)}>
            <MenuItem value="">All</MenuItem>
            <MenuItem value="open">Open</MenuItem>
            <MenuItem value="acknowledged">Acknowledged</MenuItem>
            <MenuItem value="resolved">Resolved</MenuItem>
            <MenuItem value="ignored">Ignored</MenuItem>
          </Select>
        </FormControl>
        <FormControl size="small" sx={{ minWidth: 140 }}>
          <InputLabel>Severity</InputLabel>
          <Select value={severityFilter} label="Severity" onChange={(e) => setSeverityFilter(e.target.value)}>
            <MenuItem value="">All</MenuItem>
            <MenuItem value="critical">Critical</MenuItem>
            <MenuItem value="high">High</MenuItem>
            <MenuItem value="medium">Medium</MenuItem>
            <MenuItem value="low">Low</MenuItem>
          </Select>
        </FormControl>
      </Box>

      <Paper elevation={0} sx={{ ...panelSx, overflow: 'hidden' }}>
        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow sx={{ bgcolor: '#F8FAFC' }}>
                {['Title', 'Type', 'Severity', 'Status', 'Table', 'Batch', 'Created', 'Actions'].map((h) => (
                  <TableCell key={h} sx={{ fontWeight: 700, py: 1.75 }}>{h}</TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                Array.from({ length: 8 }).map((_, i) => (
                  <TableRow key={i}>{Array.from({ length: 8 }).map((_, j) => <TableCell key={j}><Skeleton height={24} /></TableCell>)}</TableRow>
                ))
              ) : alerts.length === 0 ? (
                <TableRow><TableCell colSpan={8} align="center" sx={{ py: 6, color: 'text.secondary' }}>No alerts found</TableCell></TableRow>
              ) : alerts.map((a) => (
                <TableRow key={a.id} hover>
                  <TableCell>
                    <Typography variant="body2" fontWeight={500} sx={{ maxWidth: 280, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {a.title}
                    </Typography>
                    {a.message && (
                      <Typography variant="caption" color="text.secondary" sx={{ display: 'block', maxWidth: 280, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {a.message}
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell><Chip label={a.alert_type} size="small" variant="outlined" /></TableCell>
                  <TableCell><Chip label={a.severity} color={SEVERITY_COLORS[a.severity]} size="small" /></TableCell>
                  <TableCell><Chip label={a.status} color={STATUS_COLORS[a.status]} size="small" /></TableCell>
                  <TableCell><Typography variant="caption">{a.table_id?.slice(0, 8)}…</Typography></TableCell>
                  <TableCell><Typography variant="caption" fontFamily="monospace">{a.batch_date_hour || '—'}</Typography></TableCell>
                  <TableCell><Typography variant="caption">{new Date(a.created_at).toLocaleDateString()}</Typography></TableCell>
                  <TableCell>
                    <Stack direction="row" spacing={0.5}>
                      {a.status === 'open' && (
                        <Tooltip title="Acknowledge">
                          <IconButton size="small" onClick={() => updateStatus(a.id, 'acknowledged')}>
                            <CheckOutlined fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      )}
                      {(a.status === 'open' || a.status === 'acknowledged') && (
                        <Tooltip title="Ignore">
                          <IconButton size="small" onClick={() => updateStatus(a.id, 'ignored')}>
                            <ArchiveOutlined fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      )}
                    </Stack>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Box>
  );
}
