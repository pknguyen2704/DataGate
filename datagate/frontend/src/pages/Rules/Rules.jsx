import React from 'react';
import {
  Box, Typography, Paper, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Chip, IconButton, Tooltip, Button, Stack,
  TextField, InputAdornment, Select, FormControl, InputLabel, MenuItem,
  Skeleton,
} from '@mui/material';
import { SearchOutlined, RefreshOutlined, AddOutlined, EditOutlined, DeleteOutlined, ToggleOnOutlined } from '@mui/icons-material';
import { rulesApi } from '~/apis/api';
import { pageShellSx, panelSx } from '~/theme';

const STATUS_COLORS = { enabled: 'success', disabled: 'default', suggested: 'info', rejected: 'error' };
const SEVERITY_COLORS = { low: 'default', medium: 'warning', high: 'error', critical: 'error' };

export default function Rules() {
  const [rules, setRules] = React.useState([]);
  const [loading, setLoading] = React.useState(true);
  const [search, setSearch] = React.useState('');
  const [statusFilter, setStatusFilter] = React.useState('');

  const load = React.useCallback(() => {
    setLoading(true);
    rulesApi.list({ status: statusFilter || undefined })
      .then((r) => setRules(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [statusFilter]);

  React.useEffect(() => { load(); }, [load]);

  const filtered = rules.filter((r) =>
    !search || r.rule_name?.toLowerCase().includes(search.toLowerCase()) ||
    r.column_name?.toLowerCase().includes(search.toLowerCase())
  );

  const toggleStatus = async (rule) => {
    const next = rule.status === 'enabled' ? 'disabled' : 'enabled';
    await rulesApi.updateStatus(rule.id, next);
    load();
  };

  const deleteRule = async (id) => {
    if (!confirm('Delete this rule?')) return;
    await rulesApi.delete(id);
    load();
  };

  return (
    <Box sx={pageShellSx}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 3 }}>
        <Box>
          <Typography variant="h4" fontWeight={800} mb={0.5}>Rules</Typography>
          <Typography variant="body1" color="text.secondary">
            {filtered.length} data quality rule{filtered.length !== 1 ? 's' : ''} across all tables
          </Typography>
        </Box>
        <Stack direction="row" spacing={1}>
          <Tooltip title="Refresh">
            <IconButton onClick={load} size="small" sx={{ border: '1px solid', borderColor: 'divider' }}>
              <RefreshOutlined fontSize="small" />
            </IconButton>
          </Tooltip>
        </Stack>
      </Box>

      <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap' }}>
        <TextField
          size="small"
          placeholder="Search rules..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          sx={{ minWidth: 240 }}
          InputProps={{ startAdornment: <InputAdornment position="start"><SearchOutlined fontSize="small" /></InputAdornment> }}
        />
        <FormControl size="small" sx={{ minWidth: 140 }}>
          <InputLabel>Status</InputLabel>
          <Select value={statusFilter} label="Status" onChange={(e) => setStatusFilter(e.target.value)}>
            <MenuItem value="">All</MenuItem>
            <MenuItem value="enabled">Enabled</MenuItem>
            <MenuItem value="disabled">Disabled</MenuItem>
            <MenuItem value="suggested">Suggested</MenuItem>
            <MenuItem value="rejected">Rejected</MenuItem>
          </Select>
        </FormControl>
      </Box>

      <Paper elevation={0} sx={{ ...panelSx, overflow: 'hidden' }}>
        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow sx={{ bgcolor: '#F8FAFC' }}>
                {['Rule Name', 'Column', 'Type', 'Severity', 'Source', 'Status', 'Table', 'Actions'].map((h) => (
                  <TableCell key={h} sx={{ fontWeight: 700, py: 1.75 }}>{h}</TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                Array.from({ length: 8 }).map((_, i) => (
                  <TableRow key={i}>{Array.from({ length: 8 }).map((_, j) => <TableCell key={j}><Skeleton height={24} /></TableCell>)}</TableRow>
                ))
              ) : filtered.length === 0 ? (
                <TableRow><TableCell colSpan={8} align="center" sx={{ py: 6, color: 'text.secondary' }}>No rules found</TableCell></TableRow>
              ) : filtered.map((r) => (
                <TableRow key={r.id} hover>
                  <TableCell><Typography variant="body2" fontWeight={600}>{r.rule_name}</Typography></TableCell>
                  <TableCell><Typography variant="caption" fontFamily="monospace">{r.column_name || '(table)'}</Typography></TableCell>
                  <TableCell><Chip label={r.rule_type} size="small" variant="outlined" /></TableCell>
                  <TableCell><Chip label={r.severity} color={SEVERITY_COLORS[r.severity]} size="small" /></TableCell>
                  <TableCell><Chip label={r.source === 'manual' ? 'Manual' : 'Suggested'} size="small" variant="outlined" /></TableCell>
                  <TableCell><Chip label={r.status} color={STATUS_COLORS[r.status] || 'default'} size="small" /></TableCell>
                  <TableCell><Typography variant="caption">{r.table_id?.slice(0, 8)}…</Typography></TableCell>
                  <TableCell>
                    <Stack direction="row" spacing={0.5}>
                      <Tooltip title={r.status === 'enabled' ? 'Disable' : 'Enable'}>
                        <IconButton size="small" onClick={() => toggleStatus(r)}>
                          <ToggleOnOutlined fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete">
                        <IconButton size="small" color="error" onClick={() => deleteRule(r.id)}>
                          <DeleteOutlined fontSize="small" />
                        </IconButton>
                      </Tooltip>
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
