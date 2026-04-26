import React from 'react';
import {
  Box, Typography, Paper, Tab, Tabs, Chip, Skeleton,
  Grid, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, IconButton, Tooltip, Button,
  Stack, Divider,
} from '@mui/material';
import {
  ArrowBackOutlined, RefreshOutlined,
  CheckCircleOutlined, WarningAmberOutlined, ErrorOutlineOutlined,
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import { tablesApi } from '~/apis/api';
import { pageShellSx, panelSx, datagateColors } from '~/theme';

// ── Layer + Status helpers ────────────────────────────────────────────────────

const layerStyle = {
  bronze: { bgcolor: '#FEF3C7', color: '#92400E' },
  silver: { bgcolor: '#F3F4F6', color: '#374151' },
  gold: { bgcolor: '#FDE68A', color: '#92400E' },
};

const qualityIcon = {
  passed: <CheckCircleOutlined fontSize="small" sx={{ color: '#16A34A' }} />,
  warning: <WarningAmberOutlined fontSize="small" sx={{ color: '#F59E0B' }} />,
  failed: <ErrorOutlineOutlined fontSize="small" sx={{ color: '#EF4444' }} />,
};

// ── Stat Card ────────────────────────────────────────────────────────────────

const StatRow = ({ label, value, mono }) => (
  <Box sx={{ display: 'flex', justifyContent: 'space-between', py: 1, borderBottom: '1px solid', borderColor: 'divider' }}>
    <Typography variant="body2" color="text.secondary">{label}</Typography>
    <Typography variant="body2" fontWeight={600} fontFamily={mono ? 'monospace' : undefined}>
      {value ?? '—'}
    </Typography>
  </Box>
);

// ── Tab panels ───────────────────────────────────────────────────────────────

const OverviewTab = ({ table, latest }) => (
  <Grid container spacing={3}>
    <Grid item xs={12} md={6}>
      <Paper elevation={0} sx={{ ...panelSx, p: 2.5 }}>
        <Typography variant="subtitle2" fontWeight={700} mb={1.5}>Table Identity</Typography>
        <StatRow label="Full Name" value={table?.full_name} mono />
        <StatRow label="Layer" value={table?.layer?.toUpperCase()} />
        <StatRow label="Monitoring" value={table?.monitoring_enabled ? 'Enabled' : 'Disabled'} />
        <StatRow label="Connection" value={table?.connection_name} />
      </Paper>
    </Grid>
    <Grid item xs={12} md={6}>
      <Paper elevation={0} sx={{ ...panelSx, p: 2.5 }}>
        <Typography variant="subtitle2" fontWeight={700} mb={1.5}>Latest Batch</Typography>
        <StatRow label="Batch Date/Hour" value={table?.latest_batch_date_hour} />
        <StatRow label="Record Count" value={table?.latest_record_count?.toLocaleString()} />
        <StatRow label="Quality Status" value={table?.latest_quality_status} />
        <StatRow label="Open Alerts" value={table?.open_alert_count} />
      </Paper>
    </Grid>
  </Grid>
);

const MetadataTab = ({ tableId }) => {
  const [data, setData] = React.useState([]);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    tablesApi.getMetadata(tableId, { limit: 20 })
      .then((r) => setData(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [tableId]);

  return (
    <Paper elevation={0} sx={{ ...panelSx, overflow: 'hidden' }}>
      <TableContainer>
        <Table size="small">
          <TableHead>
            <TableRow sx={{ bgcolor: '#F8FAFC' }}>
              {['Batch Date/Hour', 'Committed At', 'Operation', 'Added Records', 'Size (bytes)', 'Total Records'].map((h) => (
                <TableCell key={h} sx={{ fontWeight: 700, py: 1.5 }}>{h}</TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <TableRow key={i}>
                  {Array.from({ length: 6 }).map((_, j) => <TableCell key={j}><Skeleton /></TableCell>)}
                </TableRow>
              ))
            ) : data.length === 0 ? (
              <TableRow><TableCell colSpan={6} align="center" sx={{ py: 4, color: 'text.secondary' }}>No metadata collected yet</TableCell></TableRow>
            ) : data.map((b) => (
              <TableRow key={b.id} hover>
                <TableCell><Typography variant="caption" fontFamily="monospace">{b.batch_date_hour || '—'}</Typography></TableCell>
                <TableCell><Typography variant="caption">{b.committed_at ? new Date(b.committed_at).toLocaleString() : '—'}</Typography></TableCell>
                <TableCell><Chip label={b.operation || '—'} size="small" /></TableCell>
                <TableCell>{b.added_records?.toLocaleString() ?? '—'}</TableCell>
                <TableCell>{b.added_data_files_size?.toLocaleString() ?? '—'}</TableCell>
                <TableCell>{b.total_records?.toLocaleString() ?? '—'}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Paper>
  );
};

const ProfilingTab = ({ tableId }) => {
  const [data, setData] = React.useState([]);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    tablesApi.getProfiling(tableId)
      .then((r) => setData(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [tableId]);

  // Group by column
  const grouped = data.reduce((acc, m) => {
    if (!acc[m.column_name]) acc[m.column_name] = { column_name: m.column_name, data_type: m.data_type, metrics: {} };
    acc[m.column_name].metrics[m.metric_name] = m.metric_value;
    return acc;
  }, {});

  const columns = Object.values(grouped);

  return (
    <Paper elevation={0} sx={{ ...panelSx, overflow: 'hidden' }}>
      <TableContainer>
        <Table size="small">
          <TableHead>
            <TableRow sx={{ bgcolor: '#F8FAFC' }}>
              {['Column', 'Type', 'Completeness', 'Min', 'Max', 'Mean', 'Distinct Count'].map((h) => (
                <TableCell key={h} sx={{ fontWeight: 700, py: 1.5 }}>{h}</TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              Array.from({ length: 6 }).map((_, i) => (
                <TableRow key={i}>
                  {Array.from({ length: 7 }).map((_, j) => <TableCell key={j}><Skeleton /></TableCell>)}
                </TableRow>
              ))
            ) : columns.length === 0 ? (
              <TableRow><TableCell colSpan={7} align="center" sx={{ py: 4, color: 'text.secondary' }}>No profiling data yet</TableCell></TableRow>
            ) : columns.map((col) => (
              <TableRow key={col.column_name} hover>
                <TableCell><Typography variant="body2" fontWeight={600}>{col.column_name}</Typography></TableCell>
                <TableCell><Chip label={col.data_type || '—'} size="small" variant="outlined" /></TableCell>
                <TableCell>
                  {col.metrics.completeness != null ? (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Box sx={{ flexGrow: 1, height: 6, bgcolor: '#E2E8F0', borderRadius: 999, overflow: 'hidden' }}>
                        <Box sx={{ width: `${col.metrics.completeness * 100}%`, height: '100%', bgcolor: col.metrics.completeness >= 0.95 ? '#16A34A' : '#F59E0B', borderRadius: 999 }} />
                      </Box>
                      <Typography variant="caption">{(col.metrics.completeness * 100).toFixed(1)}%</Typography>
                    </Box>
                  ) : '—'}
                </TableCell>
                <TableCell>{col.metrics.min ?? col.metrics.min_length ?? '—'}</TableCell>
                <TableCell>{col.metrics.max ?? col.metrics.max_length ?? '—'}</TableCell>
                <TableCell>{col.metrics.mean != null ? col.metrics.mean.toFixed(2) : '—'}</TableCell>
                <TableCell>{col.metrics.approximate_distinct_count?.toLocaleString() ?? '—'}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Paper>
  );
};

const RulesTab = ({ tableId }) => {
  const [data, setData] = React.useState([]);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    tablesApi.getRules(tableId)
      .then((r) => setData(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [tableId]);

  const statusColor = { enabled: 'success', disabled: 'default', suggested: 'info', rejected: 'error' };
  const severityColor = { low: 'default', medium: 'warning', high: 'error', critical: 'error' };

  return (
    <Paper elevation={0} sx={{ ...panelSx, overflow: 'hidden' }}>
      <TableContainer>
        <Table size="small">
          <TableHead>
            <TableRow sx={{ bgcolor: '#F8FAFC' }}>
              {['Rule Name', 'Column', 'Type', 'Severity', 'Source', 'Status', 'Created'].map((h) => (
                <TableCell key={h} sx={{ fontWeight: 700, py: 1.5 }}>{h}</TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <TableRow key={i}>
                  {Array.from({ length: 7 }).map((_, j) => <TableCell key={j}><Skeleton /></TableCell>)}
                </TableRow>
              ))
            ) : data.length === 0 ? (
              <TableRow><TableCell colSpan={7} align="center" sx={{ py: 4, color: 'text.secondary' }}>No rules defined yet</TableCell></TableRow>
            ) : data.map((r) => (
              <TableRow key={r.id} hover>
                <TableCell><Typography variant="body2" fontWeight={600}>{r.rule_name}</Typography></TableCell>
                <TableCell><Typography variant="caption" fontFamily="monospace">{r.column_name || '(table)'}</Typography></TableCell>
                <TableCell><Chip label={r.rule_type} size="small" variant="outlined" /></TableCell>
                <TableCell><Chip label={r.severity} color={severityColor[r.severity]} size="small" /></TableCell>
                <TableCell><Chip label={r.source === 'manual' ? 'Manual' : 'Suggested'} size="small" variant="outlined" /></TableCell>
                <TableCell><Chip label={r.status} color={statusColor[r.status] || 'default'} size="small" /></TableCell>
                <TableCell><Typography variant="caption">{new Date(r.created_at).toLocaleDateString()}</Typography></TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Paper>
  );
};

const QualityTab = ({ tableId }) => {
  const [data, setData] = React.useState([]);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    tablesApi.getQuality(tableId)
      .then((r) => setData(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [tableId]);

  const statusColor = { passed: 'success', warning: 'warning', failed: 'error', error: 'default' };

  return (
    <Paper elevation={0} sx={{ ...panelSx, overflow: 'hidden' }}>
      <TableContainer>
        <Table size="small">
          <TableHead>
            <TableRow sx={{ bgcolor: '#F8FAFC' }}>
              {['Batch', 'Status', 'Total Rules', 'Passed', 'Failed', 'Warning', 'AUC Score', 'Duration'].map((h) => (
                <TableCell key={h} sx={{ fontWeight: 700, py: 1.5 }}>{h}</TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <TableRow key={i}>
                  {Array.from({ length: 8 }).map((_, j) => <TableCell key={j}><Skeleton /></TableCell>)}
                </TableRow>
              ))
            ) : data.length === 0 ? (
              <TableRow><TableCell colSpan={8} align="center" sx={{ py: 4, color: 'text.secondary' }}>No validation runs yet</TableCell></TableRow>
            ) : data.map((r) => {
              const duration = r.started_at && r.finished_at
                ? `${Math.round((new Date(r.finished_at) - new Date(r.started_at)) / 1000)}s`
                : '—';
              return (
                <TableRow key={r.id} hover>
                  <TableCell><Typography variant="caption" fontFamily="monospace">{r.batch_date_hour || '—'}</Typography></TableCell>
                  <TableCell><Chip label={r.status} color={statusColor[r.status] || 'default'} size="small" /></TableCell>
                  <TableCell>{r.total_rules}</TableCell>
                  <TableCell sx={{ color: '#16A34A', fontWeight: 600 }}>{r.passed_rules}</TableCell>
                  <TableCell sx={{ color: r.failed_rules > 0 ? '#EF4444' : undefined, fontWeight: r.failed_rules > 0 ? 700 : 400 }}>{r.failed_rules}</TableCell>
                  <TableCell sx={{ color: r.warning_rules > 0 ? '#F59E0B' : undefined }}>{r.warning_rules}</TableCell>
                  <TableCell>{r.auc_score != null ? r.auc_score.toFixed(3) : '—'}</TableCell>
                  <TableCell>{duration}</TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </TableContainer>
    </Paper>
  );
};

const AnomalyTab = ({ tableId }) => {
  const [data, setData] = React.useState([]);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    tablesApi.getAnomaly(tableId)
      .then((r) => setData(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [tableId]);

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
      {loading ? (
        Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} height={120} />)
      ) : data.length === 0 ? (
        <Paper elevation={0} sx={{ ...panelSx, p: 4, textAlign: 'center' }}>
          <Typography color="text.secondary">No anomaly detection runs yet</Typography>
        </Paper>
      ) : data.map((r) => (
        <Paper key={r.id} elevation={0} sx={{ ...panelSx, p: 2.5 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
            <Box>
              <Typography variant="body2" fontWeight={700}>{r.batch_date_hour || '—'}</Typography>
              <Typography variant="caption" color="text.secondary">
                Finished: {r.finished_at ? new Date(r.finished_at).toLocaleString() : '—'}
              </Typography>
            </Box>
            <Box sx={{ textAlign: 'right' }}>
              <Typography variant="h5" fontWeight={800} color={r.auc_score >= 0.7 ? '#EF4444' : '#16A34A'}>
                {r.auc_score != null ? r.auc_score.toFixed(3) : '—'}
              </Typography>
              <Typography variant="caption" color="text.secondary">AUC Score</Typography>
            </Box>
          </Box>
          <Chip
            label={r.drift_status === 'drift_detected' ? 'Drift Detected' : r.drift_status === 'no_drift' ? 'No Drift' : r.drift_status || 'Unknown'}
            color={r.drift_status === 'drift_detected' ? 'error' : 'success'}
            size="small"
            sx={{ mb: 2 }}
          />
          {r.top_features?.length > 0 && (
            <>
              <Typography variant="caption" fontWeight={700} color="text.secondary" sx={{ display: 'block', mb: 1 }}>
                TOP CONTRIBUTING FEATURES
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.75 }}>
                {r.top_features.map((f) => (
                  <Box key={f.column} sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                    <Typography variant="caption" sx={{ minWidth: 140, fontFamily: 'monospace' }}>
                      {f.column}
                    </Typography>
                    <Box sx={{ flexGrow: 1, height: 6, bgcolor: '#E2E8F0', borderRadius: 999, overflow: 'hidden' }}>
                      <Box sx={{
                        width: `${Math.min(Math.abs(f.shap_value || 0) * 200, 100)}%`,
                        height: '100%', bgcolor: '#3B82F6', borderRadius: 999
                      }} />
                    </Box>
                    <Typography variant="caption" sx={{ minWidth: 50, textAlign: 'right' }}>
                      {f.shap_value?.toFixed(4) ?? '—'}
                    </Typography>
                  </Box>
                ))}
              </Box>
            </>
          )}
        </Paper>
      ))}
    </Box>
  );
};

const AlertsTab = ({ tableId }) => {
  const [data, setData] = React.useState([]);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    tablesApi.getAlerts(tableId)
      .then((r) => setData(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [tableId]);

  const severityColor = { low: 'default', medium: 'warning', high: 'error', critical: 'error' };
  const statusColor = { open: 'error', acknowledged: 'warning', resolved: 'success', ignored: 'default' };

  return (
    <Paper elevation={0} sx={{ ...panelSx, overflow: 'hidden' }}>
      <TableContainer>
        <Table size="small">
          <TableHead>
            <TableRow sx={{ bgcolor: '#F8FAFC' }}>
              {['Title', 'Type', 'Severity', 'Status', 'Batch', 'Created'].map((h) => (
                <TableCell key={h} sx={{ fontWeight: 700, py: 1.5 }}>{h}</TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <TableRow key={i}>{Array.from({ length: 6 }).map((_, j) => <TableCell key={j}><Skeleton /></TableCell>)}</TableRow>
              ))
            ) : data.length === 0 ? (
              <TableRow><TableCell colSpan={6} align="center" sx={{ py: 4, color: 'text.secondary' }}>No alerts</TableCell></TableRow>
            ) : data.map((a) => (
              <TableRow key={a.id} hover>
                <TableCell><Typography variant="body2" fontWeight={500}>{a.title}</Typography></TableCell>
                <TableCell><Chip label={a.alert_type} size="small" variant="outlined" /></TableCell>
                <TableCell><Chip label={a.severity} color={severityColor[a.severity]} size="small" /></TableCell>
                <TableCell><Chip label={a.status} color={statusColor[a.status]} size="small" /></TableCell>
                <TableCell><Typography variant="caption">{a.batch_date_hour || '—'}</Typography></TableCell>
                <TableCell><Typography variant="caption">{new Date(a.created_at).toLocaleDateString()}</Typography></TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Paper>
  );
};

// ── Main TableDetail Page ────────────────────────────────────────────────────

const TABS = [
  { label: 'Overview', value: 'overview' },
  { label: 'Metadata', value: 'metadata' },
  { label: 'Profiling', value: 'profiling' },
  { label: 'Rules', value: 'rules' },
  { label: 'Data Quality', value: 'quality' },
  { label: 'Anomaly', value: 'anomaly' },
  { label: 'Alerts', value: 'alerts' },
];

export default function TableDetail() {
  const { tableId } = useParams();
  const navigate = useNavigate();
  const [table, setTable] = React.useState(null);
  const [loading, setLoading] = React.useState(true);
  const [activeTab, setActiveTab] = React.useState('overview');

  const load = React.useCallback(() => {
    setLoading(true);
    tablesApi.get(tableId)
      .then((r) => setTable(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [tableId]);

  React.useEffect(() => { load(); }, [load]);

  return (
    <Box sx={pageShellSx}>
      {/* Back + Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
        <IconButton
          onClick={() => navigate('/tables')}
          size="small"
          sx={{ border: '1px solid', borderColor: 'divider' }}
        >
          <ArrowBackOutlined fontSize="small" />
        </IconButton>
        {loading ? (
          <Skeleton width={300} height={40} />
        ) : (
          <Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
              <Typography variant="h5" fontWeight={800}>
                {table?.table_name}
              </Typography>
              {table?.layer && (
                <Chip
                  label={table.layer.toUpperCase()}
                  size="small"
                  sx={{ ...layerStyle[table.layer], fontWeight: 700, fontSize: '0.7rem' }}
                />
              )}
              {table?.monitoring_enabled === false && (
                <Chip label="Monitoring Paused" size="small" color="default" variant="outlined" />
              )}
            </Box>
            <Typography variant="caption" color="text.secondary" fontFamily="monospace">
              {table?.full_name}
            </Typography>
          </Box>
        )}
        <Box sx={{ ml: 'auto' }}>
          <Tooltip title="Refresh">
            <IconButton onClick={load} size="small" sx={{ border: '1px solid', borderColor: 'divider' }}>
              <RefreshOutlined fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Tabs */}
      <Box sx={{ borderBottom: '1px solid', borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={(_, v) => setActiveTab(v)} variant="scrollable">
          {TABS.map((t) => <Tab key={t.value} label={t.label} value={t.value} />)}
        </Tabs>
      </Box>

      {/* Tab Content */}
      {activeTab === 'overview' && <OverviewTab table={table} loading={loading} />}
      {activeTab === 'metadata' && <MetadataTab tableId={tableId} />}
      {activeTab === 'profiling' && <ProfilingTab tableId={tableId} />}
      {activeTab === 'rules' && <RulesTab tableId={tableId} />}
      {activeTab === 'quality' && <QualityTab tableId={tableId} />}
      {activeTab === 'anomaly' && <AnomalyTab tableId={tableId} />}
      {activeTab === 'alerts' && <AlertsTab tableId={tableId} />}
    </Box>
  );
}
