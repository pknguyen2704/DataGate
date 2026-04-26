import React from 'react';
import {
  Box, Typography, Paper, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Chip, IconButton, Tooltip, Stack,
  Select, FormControl, InputLabel, MenuItem, Skeleton, Button,
} from '@mui/material';
import { RefreshOutlined, PlayArrowOutlined } from '@mui/icons-material';
import { jobsApi } from '~/apis/api';
import { pageShellSx, panelSx } from '~/theme';

const STATUS_COLORS = {
  pending: 'default', running: 'info', success: 'success',
  failed: 'error', skipped: 'default',
};

export default function Jobs() {
  const [jobs, setJobs] = React.useState([]);
  const [loading, setLoading] = React.useState(true);
  const [statusFilter, setStatusFilter] = React.useState('');
  const [jobFilter, setJobFilter] = React.useState('');

  const load = React.useCallback(() => {
    setLoading(true);
    jobsApi.list({ status: statusFilter || undefined, job_name: jobFilter || undefined })
      .then((r) => setJobs(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [statusFilter, jobFilter]);

  React.useEffect(() => { load(); }, [load]);

  const getDuration = (start, end) => {
    if (!start || !end) return '—';
    const secs = Math.round((new Date(end) - new Date(start)) / 1000);
    if (secs < 60) return `${secs}s`;
    return `${Math.round(secs / 60)}m ${secs % 60}s`;
  };

  const JOB_NAMES = [
    'ingest_data', 'clean_data', 'transform',
    'metadata_collection', 'profiling', 'rule_suggestion',
    'quality_validation', 'anomaly_detection',
  ];

  return (
    <Box sx={pageShellSx}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 3 }}>
        <Box>
          <Typography variant="h4" fontWeight={800} mb={0.5}>Jobs</Typography>
          <Typography variant="body1" color="text.secondary">
            Airflow pipeline execution history
          </Typography>
        </Box>
        <Tooltip title="Refresh">
          <IconButton onClick={load} size="small" sx={{ border: '1px solid', borderColor: 'divider' }}>
            <RefreshOutlined fontSize="small" />
          </IconButton>
        </Tooltip>
      </Box>

      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        <FormControl size="small" sx={{ minWidth: 200 }}>
          <InputLabel>Job Name</InputLabel>
          <Select value={jobFilter} label="Job Name" onChange={(e) => setJobFilter(e.target.value)}>
            <MenuItem value="">All Jobs</MenuItem>
            {JOB_NAMES.map((j) => <MenuItem key={j} value={j}>{j}</MenuItem>)}
          </Select>
        </FormControl>
        <FormControl size="small" sx={{ minWidth: 140 }}>
          <InputLabel>Status</InputLabel>
          <Select value={statusFilter} label="Status" onChange={(e) => setStatusFilter(e.target.value)}>
            <MenuItem value="">All</MenuItem>
            <MenuItem value="pending">Pending</MenuItem>
            <MenuItem value="running">Running</MenuItem>
            <MenuItem value="success">Success</MenuItem>
            <MenuItem value="failed">Failed</MenuItem>
            <MenuItem value="skipped">Skipped</MenuItem>
          </Select>
        </FormControl>
      </Box>

      <Paper elevation={0} sx={{ ...panelSx, overflow: 'hidden' }}>
        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow sx={{ bgcolor: '#F8FAFC' }}>
                {['Job Name', 'DAG ID', 'Status', 'Table', 'Batch', 'Started', 'Duration', 'Error'].map((h) => (
                  <TableCell key={h} sx={{ fontWeight: 700, py: 1.75 }}>{h}</TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                Array.from({ length: 8 }).map((_, i) => (
                  <TableRow key={i}>{Array.from({ length: 8 }).map((_, j) => <TableCell key={j}><Skeleton height={24} /></TableCell>)}</TableRow>
                ))
              ) : jobs.length === 0 ? (
                <TableRow><TableCell colSpan={8} align="center" sx={{ py: 6, color: 'text.secondary' }}>No job runs found</TableCell></TableRow>
              ) : jobs.map((j) => (
                <TableRow key={j.id} hover>
                  <TableCell>
                    <Typography variant="body2" fontWeight={600} fontFamily="monospace">{j.job_name}</Typography>
                  </TableCell>
                  <TableCell><Typography variant="caption" fontFamily="monospace">{j.dag_id || '—'}</Typography></TableCell>
                  <TableCell><Chip label={j.status} color={STATUS_COLORS[j.status]} size="small" /></TableCell>
                  <TableCell><Typography variant="caption">{j.table_id?.slice(0, 8) || '—'}</Typography></TableCell>
                  <TableCell><Typography variant="caption" fontFamily="monospace">{j.batch_date_hour || '—'}</Typography></TableCell>
                  <TableCell>
                    <Typography variant="caption">
                      {j.started_at ? new Date(j.started_at).toLocaleString() : '—'}
                    </Typography>
                  </TableCell>
                  <TableCell>{getDuration(j.started_at, j.finished_at)}</TableCell>
                  <TableCell>
                    {j.error_message ? (
                      <Tooltip title={j.error_message}>
                        <Typography variant="caption" color="error.main" sx={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', display: 'block' }}>
                          {j.error_message}
                        </Typography>
                      </Tooltip>
                    ) : '—'}
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
