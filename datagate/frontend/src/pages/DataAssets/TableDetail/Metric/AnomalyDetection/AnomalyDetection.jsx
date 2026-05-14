import React, { useState, useEffect } from "react";
import {
  Box, Typography, Paper, Table, TableBody, TableCell,
  TableHead, TableRow, TableContainer, Button, IconButton,
  Chip, Dialog, DialogTitle, DialogContent,
  DialogActions, TextField, MenuItem, Grid, Stack,
  Tooltip, Switch
} from "@mui/material";
import { Edit, Delete, InfoOutlined, Add } from "@mui/icons-material";
import { metricsApi } from "~/apis/metricsApi";
import { useApiResource } from "~/hooks/useApiResource";
import { format } from "date-fns";
import { StateBox } from "~/components/DataGate/Page";

const SEVERITY_COLORS = {
  warning: "warning",
  critical: "error"
};

const AnomalyDetection = ({ tableId, canManage, searchQuery, filters, addTrigger }) => {
  const [openDialog, setOpenDialog] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({});

  const anomalyRes = useApiResource(() => metricsApi.listAnomaly(tableId), [tableId]);

  useEffect(() => {
    if (addTrigger > 0) {
      handleOpenDialog();
    }
  }, [addTrigger]);

  const handleOpenDialog = (item = null) => {
    setEditingId(item?.id || null);
    if (item) {
      setFormData({ ...item });
    } else {
      setFormData({
        table_id: tableId,
        metric_name: 'auc_score',
        severity_level: 'warning',
        is_active: true,
        auc_threshold: 0.8,
        description: ''
      });
    }
    setOpenDialog(true);
  };

  const handleSave = async () => {
    try {
      const data = { ...formData };
      if (editingId) {
        await metricsApi.updateAnomaly(editingId, data);
      } else {
        await metricsApi.createAnomaly(data);
      }

      setOpenDialog(false);
      anomalyRes.reload();
    } catch (err) {
      console.error("Save failed:", err);
      alert(err.response?.data?.detail || "Failed to save threshold");
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to permanently delete this threshold?")) return;
    try {
      await metricsApi.deleteAnomaly(id);
      anomalyRes.reload();
    } catch (err) {
      alert("Delete failed");
    }
  };

  const handleToggleActive = async (item) => {
    try {
      const { id, updated_at, created_at, created_by_user, last_modified_by_user, ...data } = item;
      await metricsApi.updateAnomaly(id, { ...data, is_active: !item.is_active });
      anomalyRes.reload();
    } catch (err) {
      alert("Toggle status failed");
    }
  };

  const filteredData = (anomalyRes.data?.items || []).filter(item => {
    const matchesSearch = "anomaly score".includes(searchQuery.toLowerCase()) || 
                         (item.description || "").toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = filters.status === "" || (filters.status === "active" ? item.is_active : !item.is_active);
    const matchesSeverity = filters.severity === "" || item.severity_level === filters.severity;
    return matchesSearch && matchesStatus && matchesSeverity;
  });

  return (
    <>
      <StateBox
        loading={anomalyRes.loading}
        error={anomalyRes.error}
        empty={!filteredData.length && !searchQuery && !filters.status && !filters.severity}
        onReload={anomalyRes.reload}
      >
        <TableContainer component={Paper} variant="outlined" sx={{ border: 'none' }}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Metric</TableCell>
                <TableCell>AUC Threshold</TableCell>
                <TableCell>Severity</TableCell>
                <TableCell>Description</TableCell>
                <TableCell>Created By</TableCell>
                <TableCell>Updated By</TableCell>
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
                    <TableCell>
                      <Typography variant="body2" fontWeight={600}>Anomaly Score</Typography>
                    </TableCell>
                    <TableCell>{row.auc_threshold}</TableCell>
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
                      <Typography variant="body2">
                        {row.description || "-"}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">{row.created_by_user?.full_name || row.created_by_user?.username || 'System'}</Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">{row.last_modified_by_user?.full_name || row.last_modified_by_user?.username || 'System'}</Typography>
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
                        {canManage && (
                          <>
                            <IconButton size="small" color="primary" onClick={() => handleOpenDialog(row)}>
                              <Edit fontSize="small" />
                            </IconButton>
                            <IconButton size="small" color="error" onClick={() => handleDelete(row.id)}>
                              <Delete fontSize="small" />
                            </IconButton>
                          </>
                        )}
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
                type="number"
                label="AUC Threshold (0.0 - 1.0)"
                value={formData.auc_threshold || ''}
                onChange={(e) => setFormData({ ...formData, auc_threshold: parseFloat(e.target.value) })}
                inputProps={{ step: 0.01, min: 0, max: 1 }}
                required
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
    </>
  );
};

export default AnomalyDetection;