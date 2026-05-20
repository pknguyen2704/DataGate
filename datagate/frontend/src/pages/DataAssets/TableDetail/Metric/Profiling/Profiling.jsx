import React, { useState, useEffect, useCallback } from "react";
import {
  Box, Typography, Paper, Table, TableBody, TableCell,
  TableHead, TableRow, TableContainer, Button, IconButton,
  Chip, Dialog, DialogTitle, DialogContent,
  DialogActions, TextField, MenuItem, Grid, Stack,
  Tooltip, Switch
} from "@mui/material";
import { Edit, Delete, InfoOutlined, Add, VisibilityOutlined } from "@mui/icons-material";
import { metricsApi } from "~/apis/metricsApi";
import { useApiResource } from "~/hooks/useApiResource";
import { StateBox } from "~/components/Common/DataDisplay";

import { useConfirm } from "material-ui-confirm";

const SEVERITY_COLORS = {
  warning: "warning",
  critical: "error"
};

const METRIC_TYPES = [
  { value: "completeness", label: "Completeness (%)" },
  { value: "distinctness", label: "Distinctness (%)" },
  { value: "mean", label: "Mean" },
  { value: "standard_deviation", label: "Standard Deviation" },
  { value: "minimum", label: "Minimum" },
  { value: "maximum", label: "Maximum" },
  { value: "min_length", label: "Min Length" },
  { value: "max_length", label: "Max Length" },
];

const Profiling = ({ tableId, canManage, searchQuery, filters, addTrigger }) => {
  const confirm = useConfirm();
  const [openDialog, setOpenDialog] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({});
  const [openDetailDialog, setOpenDetailDialog] = useState(false);
  const [selectedDetail, setSelectedDetail] = useState(null);

  const profilingRes = useApiResource(() => metricsApi.listProfiling(tableId), [tableId]);

  const handleOpenDialog = useCallback((item = null) => {
    setEditingId(item?.id || null);
    if (item) {
      setFormData({ ...item });
    } else {
      setFormData({
        table_id: tableId,
        column_name: '',
        metric_name: '',
        severity_level: 'warning',
        is_active: true,
        min_threshold: '',
        max_threshold: '',
        description: ''
      });
    }
    setOpenDialog(true);
  }, [tableId]);

  const handleOpenDetail = (row) => {
    setSelectedDetail(row);
    setOpenDetailDialog(true);
  };

  const handleEditFromDetail = () => {
    setOpenDetailDialog(false);
    handleOpenDialog(selectedDetail);
  };

  const handleDeleteFromDetail = () => {
    setOpenDetailDialog(false);
    handleDelete(selectedDetail.id);
  };

  useEffect(() => {
    if (addTrigger > 0) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      handleOpenDialog();
    }
  }, [addTrigger, handleOpenDialog]);

  const handleSave = async () => {
    try {
      const data = { ...formData };
      if (data.min_threshold === '') data.min_threshold = null;
      if (data.max_threshold === '') data.max_threshold = null;

      if (editingId) {
        await metricsApi.updateProfiling(editingId, data);
      } else {
        await metricsApi.createProfiling(data);
      }

      setOpenDialog(false);
      profilingRes.reload();
    } catch (error) {
      console.error("Save failed:", error);
      alert(error.response?.data?.detail || "Failed to save threshold");
    }
  };

  const handleDelete = (id) => {
    confirm({
      title: "Delete Threshold",
      description: "Are you sure you want to permanently delete this threshold?",
      confirmationText: "Delete",
      cancellationText: "Cancel",
      confirmationButtonProps: { color: "error", variant: "contained" }
    })
      .then(async () => {
        try {
          await metricsApi.deleteProfiling(id);
          profilingRes.reload();
        } catch (error) {
          console.error(error);
          alert("Delete failed");
        }
      })
      .catch(() => {});
  };

  const handleToggleActive = async (item) => {
    try {
      const newActive = !item.is_active;
      const data = { ...item, is_active: newActive };
      delete data.updated_at;
      delete data.created_at;
      delete data.created_by_user;
      delete data.last_modified_by_user;
      await metricsApi.updateProfiling(data.id, data);
      profilingRes.reload();
      if (selectedDetail && selectedDetail.id === item.id) {
        setSelectedDetail(prev => ({ ...prev, is_active: newActive }));
      }
    } catch (error) {
      console.error(error);
      alert("Toggle status failed");
    }
  };

  const filteredData = (profilingRes.data?.items || []).filter(item => {
    const metricLabel = METRIC_TYPES.find(m => m.value === item.metric_name)?.label || item.metric_name;
    const matchesSearch = (item.column_name || "").toLowerCase().includes(searchQuery.toLowerCase()) ||
                         metricLabel.toLowerCase().includes(searchQuery.toLowerCase()) || 
                         (item.description || "").toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = filters.status === "" || (filters.status === "active" ? item.is_active : !item.is_active);
    const matchesSeverity = filters.severity === "" || item.severity_level === filters.severity;
    return matchesSearch && matchesStatus && matchesSeverity;
  });

  return (
    <>
      <StateBox
        loading={profilingRes.loading}
        error={profilingRes.error}
        empty={!filteredData.length && !searchQuery && !filters.status && !filters.severity}
        onReload={profilingRes.reload}
      >
        <TableContainer component={Paper} variant="outlined" sx={{ border: 'none' }}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Column</TableCell>
                <TableCell>Metric</TableCell>
                <TableCell>Min</TableCell>
                <TableCell>Max</TableCell>
                <TableCell>Severity</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredData.length === 0 ? (
                <TableRow><TableCell colSpan={7} align="center" sx={{ py: 4, color: 'text.secondary' }}>No records found</TableCell></TableRow>
              ) : (
                filteredData.map((row) => (
                  <TableRow key={row.id} hover>
                    <TableCell>{row.column_name}</TableCell>
                    <TableCell>
                      <Typography variant="body2" fontWeight={600}>
                        {METRIC_TYPES.find(m => m.value === row.metric_name)?.label || row.metric_name}
                      </Typography>
                    </TableCell>
                    <TableCell>{row.min_threshold ?? '-'}</TableCell>
                    <TableCell>{row.max_threshold ?? '-'}</TableCell>
                    <TableCell>
                      <Chip
                        label={row.severity_level}
                        size="small"
                        color={SEVERITY_COLORS[row.severity_level]}
                        variant="outlined"
                        sx={{ fontWeight: 600, textTransform: 'capitalize' }}
                      />
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Switch 
                          size="small" 
                          checked={row.is_active} 
                          onChange={() => handleToggleActive(row)}
                          color="success"
                          disabled={!canManage}
                        />
                        <Chip 
                          label={row.is_active ? "Active" : "Inactive"} 
                          size="small" 
                          variant="outlined" 
                          color={row.is_active ? "success" : "default"}
                          sx={{ ml: 1, border: 'none', fontWeight: 600 }}
                        />
                      </Box>
                    </TableCell>
                    <TableCell align="right">
                      <Stack direction="row" spacing={0.5} justifyContent="flex-end">
                        <Tooltip title="View Details">
                          <IconButton size="small" color="primary" onClick={() => handleOpenDetail(row)}>
                            <VisibilityOutlined fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </Stack>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </StateBox>

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{editingId ? "Edit Threshold" : "Create Threshold"}</DialogTitle>
        <DialogContent dividers>
          <Grid container spacing={2} sx={{ mt: 0.5 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Column Name"
                value={formData.column_name || ''}
                onChange={(e) => setFormData({ ...formData, column_name: e.target.value })}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                select
                fullWidth
                label="Metric Name"
                value={formData.metric_name || ''}
                onChange={(e) => setFormData({ ...formData, metric_name: e.target.value })}
                required
              >
                {METRIC_TYPES.map(m => (
                  <MenuItem key={m.value} value={m.value}>{m.label}</MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={6}>
              <TextField
                fullWidth
                type="number"
                label="Min Threshold"
                value={formData.min_threshold ?? ''}
                onChange={(e) => setFormData({ ...formData, min_threshold: e.target.value })}
                placeholder="None"
              />
            </Grid>
            <Grid item xs={6}>
              <TextField
                fullWidth
                type="number"
                label="Max Threshold"
                value={formData.max_threshold ?? ''}
                onChange={(e) => setFormData({ ...formData, max_threshold: e.target.value })}
                placeholder="None"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                select
                fullWidth
                label="Severity Level"
                value={formData.severity_level || 'warning'}
                onChange={(e) => setFormData({ ...formData, severity_level: e.target.value })}
              >
                <MenuItem value="warning">Warning</MenuItem>
                <MenuItem value="critical">Critical</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Description"
                value={formData.description || ''}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button onClick={handleSave} variant="contained" color="primary">Save</Button>
        </DialogActions>
      </Dialog>

      {/* Detail Dialog */}
      <Dialog open={openDetailDialog} onClose={() => setOpenDetailDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ fontWeight: 800, color: 'primary.main', display: 'flex', alignItems: 'center', gap: 1 }}>
          <InfoOutlined color="primary" /> Threshold Details
        </DialogTitle>
        <DialogContent dividers>
          {selectedDetail && (
            <Grid container spacing={2} sx={{ mt: 0.5 }}>
              <Grid item xs={12}>
                <Paper variant="outlined" sx={{ p: 2, borderRadius: 1.5, bgcolor: 'action.hover', border: '1px solid', borderColor: 'divider' }}>
                  <Typography variant="caption" color="text.secondary" fontWeight={700}>COLUMN & METRIC</Typography>
                  <Typography variant="h6" fontWeight={800} color="primary.main" sx={{ mt: 0.5 }}>
                    {selectedDetail.column_name}
                  </Typography>
                  <Typography variant="body2" fontWeight={600} color="text.secondary">
                    {METRIC_TYPES.find(m => m.value === selectedDetail.metric_name)?.label || selectedDetail.metric_name}
                  </Typography>
                </Paper>
              </Grid>

              <Grid item xs={6}>
                <Paper variant="outlined" sx={{ p: 2, borderRadius: 1.5 }}>
                  <Typography variant="caption" color="text.secondary" fontWeight={700}>MIN THRESHOLD</Typography>
                  <Typography variant="body1" fontWeight={600} sx={{ mt: 0.5 }}>
                    {selectedDetail.min_threshold ?? 'None'}
                  </Typography>
                </Paper>
              </Grid>

              <Grid item xs={6}>
                <Paper variant="outlined" sx={{ p: 2, borderRadius: 1.5 }}>
                  <Typography variant="caption" color="text.secondary" fontWeight={700}>MAX THRESHOLD</Typography>
                  <Typography variant="body1" fontWeight={600} sx={{ mt: 0.5 }}>
                    {selectedDetail.max_threshold ?? 'None'}
                  </Typography>
                </Paper>
              </Grid>

              <Grid item xs={12}>
                <Paper variant="outlined" sx={{ p: 2, borderRadius: 1.5 }}>
                  <Typography variant="caption" color="text.secondary" fontWeight={700}>SEVERITY LEVEL</Typography>
                  <Box sx={{ mt: 0.5 }}>
                    <Chip
                      label={selectedDetail.severity_level}
                      size="small"
                      color={SEVERITY_COLORS[selectedDetail.severity_level]}
                      variant="outlined"
                      sx={{ fontWeight: 600, textTransform: 'capitalize' }}
                    />
                  </Box>
                </Paper>
              </Grid>

              <Grid item xs={6}>
                <Paper variant="outlined" sx={{ p: 2, borderRadius: 1.5 }}>
                  <Typography variant="caption" color="text.secondary" fontWeight={700}>CREATED BY</Typography>
                  <Typography variant="body2" fontWeight={600} sx={{ mt: 0.5 }}>
                    {selectedDetail.created_by_user?.full_name || selectedDetail.created_by_user?.username || 'System'}
                  </Typography>
                </Paper>
              </Grid>

              <Grid item xs={6}>
                <Paper variant="outlined" sx={{ p: 2, borderRadius: 1.5 }}>
                  <Typography variant="caption" color="text.secondary" fontWeight={700}>UPDATED BY</Typography>
                  <Typography variant="body2" fontWeight={600} sx={{ mt: 0.5 }}>
                    {selectedDetail.last_modified_by_user?.full_name || selectedDetail.last_modified_by_user?.username || 'System'}
                  </Typography>
                </Paper>
              </Grid>

              <Grid item xs={12}>
                <Paper variant="outlined" sx={{ p: 2, borderRadius: 1.5 }}>
                  <Typography variant="caption" color="text.secondary" fontWeight={700}>DESCRIPTION</Typography>
                  <Typography variant="body2" sx={{ mt: 0.5 }}>
                    {selectedDetail.description || 'No description provided.'}
                  </Typography>
                </Paper>
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions sx={{ p: 2, justifyContent: 'space-between' }}>
          <Button onClick={() => setOpenDetailDialog(false)} color="inherit">Close</Button>
          {canManage && selectedDetail && (
            <Stack direction="row" spacing={2} alignItems="center">
              <Box sx={{ display: 'flex', alignItems: 'center', mr: 1 }}>
                <Switch
                  size="small"
                  checked={selectedDetail.is_active}
                  onChange={() => handleToggleActive(selectedDetail)}
                  color="success"
                />
                <Chip
                  label={selectedDetail.is_active ? "Active" : "Inactive"}
                  size="small"
                  variant="outlined"
                  color={selectedDetail.is_active ? "success" : "default"}
                  sx={{ ml: 1, border: 'none', fontWeight: 600 }}
                />
              </Box>
              <Button
                variant="outlined"
                startIcon={<Edit fontSize="small" />}
                onClick={handleEditFromDetail}
              >
                Edit
              </Button>
              <Button
                variant="contained"
                color="error"
                startIcon={<Delete fontSize="small" />}
                onClick={handleDeleteFromDetail}
              >
                Delete
              </Button>
            </Stack>
          )}
        </DialogActions>
      </Dialog>
    </>
  );
};

export default Profiling;
