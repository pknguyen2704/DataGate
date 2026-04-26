import React from 'react';
import {
  Box, Typography, Paper, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, Chip, TextField,
  InputAdornment, MenuItem, Select, FormControl, InputLabel,
  Button, Skeleton, Pagination, Stack, Tooltip, IconButton,
} from '@mui/material';
import {
  SearchOutlined, AddOutlined, RefreshOutlined,
  OpenInNewOutlined,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { tablesApi } from '~/apis/api';
import { pageShellSx, panelSx } from '~/theme';

// ── Status Chip ──────────────────────────────────────────────────────────────

const QualityChip = ({ status }) => {
  const map = {
    passed: { label: 'Passed', color: 'success' },
    warning: { label: 'Warning', color: 'warning' },
    failed: { label: 'Failed', color: 'error' },
    error: { label: 'Error', color: 'error' },
  };
  const cfg = map[status] || { label: 'No data', color: 'default' };
  return <Chip label={cfg.label} color={cfg.color} size="small" />;
};

const LayerChip = ({ layer }) => {
  const colorMap = { bronze: '#92400E', silver: '#4B5563', gold: '#B45309' };
  const bgMap = { bronze: '#FEF3C7', silver: '#F3F4F6', gold: '#FDE68A' };
  return (
    <Chip
      label={layer?.toUpperCase()}
      size="small"
      sx={{
        bgcolor: bgMap[layer] || '#F3F4F6',
        color: colorMap[layer] || '#374151',
        fontWeight: 700,
        fontSize: '0.7rem',
      }}
    />
  );
};

// ── Tables Page ──────────────────────────────────────────────────────────────

export default function Tables() {
  const navigate = useNavigate();
  const [tables, setTables] = React.useState([]);
  const [total, setTotal] = React.useState(0);
  const [loading, setLoading] = React.useState(true);
  const [page, setPage] = React.useState(1);
  const [search, setSearch] = React.useState('');
  const [layer, setLayer] = React.useState('');
  const pageSize = 15;

  const load = React.useCallback(() => {
    setLoading(true);
    tablesApi.list({ page, page_size: pageSize, search: search || undefined, layer: layer || undefined })
      .then((res) => {
        setTables(res.data.items || []);
        setTotal(res.data.total || 0);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [page, search, layer]);

  React.useEffect(() => { load(); }, [load]);

  const handleSearchChange = (e) => {
    setSearch(e.target.value);
    setPage(1);
  };

  return (
    <Box sx={pageShellSx}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 3 }}>
        <Box>
          <Typography variant="h4" fontWeight={800} mb={0.5}>Tables</Typography>
          <Typography variant="body1" color="text.secondary">
            {total} registered table{total !== 1 ? 's' : ''} under monitoring
          </Typography>
        </Box>
        <Stack direction="row" spacing={1}>
          <Tooltip title="Refresh">
            <IconButton onClick={load} size="small" sx={{ border: '1px solid', borderColor: 'divider' }}>
              <RefreshOutlined fontSize="small" />
            </IconButton>
          </Tooltip>
          <Button variant="contained" startIcon={<AddOutlined />} onClick={() => navigate('/tables/new')}>
            Register Table
          </Button>
        </Stack>
      </Box>

      {/* Filters */}
      <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap' }}>
        <TextField
          size="small"
          placeholder="Search tables..."
          value={search}
          onChange={handleSearchChange}
          sx={{ minWidth: 260 }}
          InputProps={{
            startAdornment: <InputAdornment position="start"><SearchOutlined fontSize="small" /></InputAdornment>,
          }}
        />
        <FormControl size="small" sx={{ minWidth: 140 }}>
          <InputLabel>Layer</InputLabel>
          <Select value={layer} label="Layer" onChange={(e) => { setLayer(e.target.value); setPage(1); }}>
            <MenuItem value="">All layers</MenuItem>
            <MenuItem value="bronze">Bronze</MenuItem>
            <MenuItem value="silver">Silver</MenuItem>
            <MenuItem value="gold">Gold</MenuItem>
          </Select>
        </FormControl>
      </Box>

      {/* Table */}
      <Paper elevation={0} sx={{ ...panelSx, overflow: 'hidden' }}>
        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow sx={{ bgcolor: '#F8FAFC' }}>
                <TableCell sx={{ fontWeight: 700, py: 1.75 }}>Table</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Layer</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Connection</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Latest Batch</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Records</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Quality</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Alerts</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Monitor</TableCell>
                <TableCell />
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                Array.from({ length: 8 }).map((_, i) => (
                  <TableRow key={i}>
                    {Array.from({ length: 9 }).map((_, j) => (
                      <TableCell key={j}><Skeleton height={24} /></TableCell>
                    ))}
                  </TableRow>
                ))
              ) : tables.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={9} align="center" sx={{ py: 6, color: 'text.secondary' }}>
                    No tables found. Register your first table to start monitoring.
                  </TableCell>
                </TableRow>
              ) : (
                tables.map((t) => (
                  <TableRow
                    key={t.id}
                    hover
                    sx={{ cursor: 'pointer', '&:hover': { bgcolor: '#F8FAFC' } }}
                    onClick={() => navigate(`/tables/${t.id}`)}
                  >
                    <TableCell>
                      <Box>
                        <Typography variant="body2" fontWeight={600}>{t.table_name}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          {t.catalog_name}.{t.schema_name}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell><LayerChip layer={t.layer} /></TableCell>
                    <TableCell>
                      <Typography variant="caption" color="text.secondary">{t.connection_name || '—'}</Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="caption">{t.latest_batch_date_hour || 'No data'}</Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {t.latest_record_count != null
                          ? t.latest_record_count.toLocaleString()
                          : '—'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <QualityChip status={t.latest_quality_status} />
                    </TableCell>
                    <TableCell>
                      {t.open_alert_count > 0 ? (
                        <Chip label={t.open_alert_count} color="error" size="small" />
                      ) : (
                        <Typography variant="caption" color="text.secondary">0</Typography>
                      )}
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={t.monitoring_enabled ? 'Active' : 'Paused'}
                        color={t.monitoring_enabled ? 'success' : 'default'}
                        size="small"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      <Tooltip title="Open detail">
                        <IconButton
                          size="small"
                          onClick={(e) => { e.stopPropagation(); navigate(`/tables/${t.id}`); }}
                        >
                          <OpenInNewOutlined fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Pagination */}
        {total > pageSize && (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 2, borderTop: '1px solid', borderColor: 'divider' }}>
            <Pagination
              count={Math.ceil(total / pageSize)}
              page={page}
              onChange={(_, v) => setPage(v)}
              color="primary"
              size="small"
            />
          </Box>
        )}
      </Paper>
    </Box>
  );
}
