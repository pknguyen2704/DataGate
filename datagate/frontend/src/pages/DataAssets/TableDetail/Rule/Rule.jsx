import React, { useState } from "react";
import { 
  Box, Typography, Paper, Table, TableBody, TableCell, 
  TableHead, TableRow, TableContainer, Button, IconButton, 
  Chip, Dialog, DialogTitle, DialogContent, 
  DialogActions, TextField, MenuItem, Grid, Stack,
  Tooltip, Alert, FormControl, InputLabel, Select, TablePagination, Switch, CircularProgress
} from "@mui/material";
import {
  Add, Edit, Delete, InfoOutlined,
  CheckCircle, DoNotDisturb, HourglassEmpty, Search, FilterList, VisibilityOutlined
} from "@mui/icons-material";
import { useParams } from "react-router-dom";
import { rulesApi } from "~/apis/rulesApi";
import { useApiResource } from "~/hooks/useApiResource";
import { useSelector } from "react-redux";
import { StateBox } from "~/components/Common/DataDisplay";

import { useConfirm } from "material-ui-confirm";

const STATUS_COLORS = {
  active: "success",
  inactive: "default"
};

const SEVERITY_COLORS = {
  warning: "warning",
  critical: "error"
};

const Rule = () => {
  const confirm = useConfirm();
  const { tableId } = useParams();
  const { user } = useSelector(state => state.auth);
  
  // Filters state
  const [filters, setFilters] = useState({
    search: "",
    source: "",
    rule_status: "",
    severity_level: ""
  });

  // UI State
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({});
  const [openDetailDialog, setOpenDetailDialog] = useState(false);
  const [selectedDetail, setSelectedDetail] = useState(null);

  // Permissions
  const isAdmin = user?.roles?.some(r => r === "Admin" || r?.name === "Admin");
  
  const canManage = isAdmin || user?.permissions?.some(p => p === "rule:manage" || p?.code === "rule:manage");
  const canCreateUpdate = canManage;
  const canApproveDeactivate = canManage;
  const canDelete = canManage;

  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);

  // API Resource
  const rulesRes = useApiResource(() => rulesApi.list({ 
    table_id: tableId, 
    ...filters,
    page: page + 1,
    page_size: pageSize
  }), [tableId, filters, page, pageSize]);

  const handleFilterChange = (name, value) => {
    setFilters(prev => ({ ...prev, [name]: value }));
    setPage(0); // Reset to first page on filter change
  };

  const [isEditing, setIsEditing] = useState(false);
  const [loadingDetail, setLoadingDetail] = useState(false);

  const handleOpenDetail = async (row) => {
    setEditingId(row.id);
    setSelectedDetail(row);
    setIsEditing(false);
    setOpenDetailDialog(true);
    setLoadingDetail(true);
    try {
      const res = await rulesApi.get(row.id);
      setSelectedDetail(res.data);
      setFormData(res.data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoadingDetail(false);
    }
  };

  const handleCreateNew = () => {
    setEditingId(null);
    setSelectedDetail(null);
    setFormData({
      table_id: tableId,
      column_name: "",
      constraint_name: "",
      source: "manual",
      severity_level: "warning",
      frequency: 1,
      code_for_constraint: "",
      description: ""
    });
    setIsEditing(true);
    setOpenDetailDialog(true);
  };

  const handleEditFromDetail = () => {
    setFormData({ ...selectedDetail });
    setIsEditing(true);
  };

  const handleCancelEdit = () => {
    if (selectedDetail) {
      setIsEditing(false);
    } else {
      setOpenDetailDialog(false);
    }
  };

  const handleSave = async () => {
    try {
      if (editingId) {
        const res = await rulesApi.update(editingId, formData);
        setSelectedDetail(res.data);
        setIsEditing(false);
        rulesRes.reload();
      } else {
        await rulesApi.create(formData);
        setOpenDetailDialog(false);
        rulesRes.reload();
      }
    } catch (error) {
      alert(error.response?.data?.detail || "Failed to save rule");
    }
  };

  const handleDelete = (id) => {
    confirm({
      title: "Delete Rule",
      description: "Are you sure you want to permanently delete this rule?",
      confirmationText: "Delete",
      cancellationText: "Cancel",
      confirmationButtonProps: { color: "error", variant: "contained" }
    })
      .then(async () => {
        try {
          await rulesApi.delete(id);
          setOpenDetailDialog(false);
          rulesRes.reload();
        } catch (error) {
          console.error(error);
          alert("Delete failed");
        }
      })
      .catch(() => {});
  };

  const handleToggleActive = async (rule) => {
    try {
      const newActive = !rule.is_active;
      if (rule.is_active) {
        await rulesApi.deactivate(rule.id);
      } else {
        await rulesApi.approve(rule.id);
      }
      rulesRes.reload();
      if (selectedDetail && selectedDetail.id === rule.id) {
        setSelectedDetail(prev => ({ ...prev, is_active: newActive }));
      }
    } catch (error) {
      console.error(error);
      alert("Toggle status failed");
    }
  };


  return (
    <Box sx={{ p: 3 }}>
      {/* Header & Main Actions */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h6" fontWeight={700}>Data Quality Rules</Typography>
        <Stack direction="row" spacing={1}>
          {canCreateUpdate && (
            <Button variant="contained" startIcon={<Add />} onClick={handleCreateNew}>Add Rule</Button>
          )}
        </Stack>
      </Box>

      {/* Filter Bar */}
      <Paper variant="outlined" sx={{ p: 2, mb: 3, borderRadius: 2, bgcolor: 'background.default' }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={3}>
            <FormControl fullWidth size="small">
              <InputLabel>Source</InputLabel>
              <Select value={filters.source} label="Source" onChange={(e) => handleFilterChange("source", e.target.value)}>
                <MenuItem value="">All Sources</MenuItem>
                <MenuItem value="manual">Manual</MenuItem>
                <MenuItem value="system">System</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth size="small">
              <InputLabel>Status</InputLabel>
              <Select value={filters.rule_status} label="Status" onChange={(e) => handleFilterChange("rule_status", e.target.value)}>
                <MenuItem value="">All Status</MenuItem>
                <MenuItem value="active">Active Only</MenuItem>
                <MenuItem value="inactive">Inactive Only</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth size="small">
              <InputLabel>Severity</InputLabel>
              <Select value={filters.severity_level} label="Severity" onChange={(e) => handleFilterChange("severity_level", e.target.value)}>
                <MenuItem value="">All Severities</MenuItem>
                <MenuItem value="warning">Warning</MenuItem>
                <MenuItem value="critical">Critical</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={3}>
            <Button 
              fullWidth 
              variant="contained" 
              startIcon={<FilterList />} 
              onClick={() => rulesRes.reload()}
              sx={{ 
                bgcolor: 'primary.main', 
                color: 'white',
                '&:hover': { bgcolor: 'primary.dark' },
                fontWeight: 700,
                borderRadius: 1.5
              }}
            >
              Filter
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Rules Table */}
      <StateBox 
        loading={rulesRes.loading} 
        error={rulesRes.error} 
        empty={!(rulesRes.data?.items || []).length}
        onReload={rulesRes.reload}
      >
        <TableContainer component={Paper} variant="outlined" sx={{ borderRadius: 2, overflow: 'hidden' }}>
          <Table size="small">
            <TableHead>
              <TableRow sx={{ bgcolor: 'primary.main' }}>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Column</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Constraint</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Severity</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Status</TableCell>
                <TableCell align="right" sx={{ color: 'white', fontWeight: 'bold' }}>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {(rulesRes.data?.items || []).map((rule) => {
                return (
                  <TableRow key={rule.id} hover>
                    <TableCell>
                      <Typography variant="body2" fontWeight={600}>{rule.column_name}</Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" fontWeight={500} sx={{ maxWidth: 300, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {rule.constraint_name || rule.code_for_constraint}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={rule.severity_level} 
                        size="small" 
                        color={rule.severity_level === 'critical' ? 'error' : 'warning'} 
                        variant="outlined"
                        sx={{ fontWeight: 600, textTransform: 'capitalize' }}
                      />
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Switch 
                          size="small" 
                          checked={rule.is_active} 
                          onChange={() => handleToggleActive(rule)}
                          color="success"
                          disabled={!canApproveDeactivate}
                        />
                        <Chip 
                          label={rule.is_active ? "Active" : "Inactive"} 
                          size="small" 
                          variant="outlined" 
                          color={rule.is_active ? "success" : "default"}
                          sx={{ ml: 1, border: 'none', fontWeight: 600 }}
                        />
                      </Box>
                    </TableCell>
                    <TableCell align="right">
                      <Stack direction="row" spacing={0.5} justifyContent="flex-end">
                        <Tooltip title="View Details">
                          <IconButton size="small" color="primary" onClick={() => handleOpenDetail(rule)}>
                            <VisibilityOutlined fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </Stack>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
          <TablePagination
            rowsPerPageOptions={[5, 10, 25]}
            component="div"
            count={rulesRes.data?.total || 0}
            rowsPerPage={pageSize}
            page={page}
            onPageChange={(e, newPage) => setPage(newPage)}
            onRowsPerPageChange={(e) => {
              setPageSize(parseInt(e.target.value, 10));
              setPage(0);
            }}
          />
        </TableContainer>
      </StateBox>

      {/* Unified Detail & Edit Dialog */}
      <Dialog open={openDetailDialog} onClose={() => setOpenDetailDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ fontWeight: 800, color: 'primary.main', display: 'flex', alignItems: 'center', gap: 1 }}>
          {isEditing ? (
            <>
              <Edit color="primary" /> {editingId ? "Edit Data Rule" : "Create Data Rule"}
            </>
          ) : (
            <>
              <InfoOutlined color="primary" /> Rule Details
            </>
          )}
        </DialogTitle>
        <DialogContent dividers>
          {loadingDetail && !isEditing ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 5 }}>
              <CircularProgress />
            </Box>
          ) : isEditing ? (
            <Grid container spacing={2} sx={{ mt: 0.5 }}>
              <Grid item xs={12} md={6}>
                <TextField 
                  fullWidth label="Column Name" required
                  value={formData.column_name || ''} onChange={(e) => setFormData({...formData, column_name: e.target.value})}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField 
                  fullWidth label="Constraint Name"
                  value={formData.constraint_name || ''} onChange={(e) => setFormData({...formData, constraint_name: e.target.value})}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField 
                  fullWidth label="Constraint Code" required
                  placeholder="e.g. isComplete('column_name')"
                  helperText="Please read Deequ documentation for syntax: https://github.com/awslabs/deequ"
                  value={formData.code_for_constraint || ''} onChange={(e) => setFormData({...formData, code_for_constraint: e.target.value})}
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  select fullWidth label="Severity"
                  value={formData.severity_level || 'warning'} onChange={(e) => setFormData({...formData, severity_level: e.target.value})}
                >
                  <MenuItem value="warning">Warning</MenuItem>
                  <MenuItem value="critical">Critical</MenuItem>
                </TextField>
              </Grid>
              <Grid item xs={6}>
                <TextField 
                  fullWidth type="number" label="Frequency"
                  value={formData.frequency || 1} onChange={(e) => setFormData({...formData, frequency: parseInt(e.target.value, 10) || 1})}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField 
                  fullWidth multiline rows={3} label="Rule Description"
                  value={formData.description || ''} onChange={(e) => setFormData({...formData, description: e.target.value})}
                />
              </Grid>
            </Grid>
          ) : selectedDetail ? (
            <Grid container spacing={2} sx={{ mt: 0.5 }}>
              <Grid item xs={12}>
                <Paper variant="outlined" sx={{ p: 2, borderRadius: 1.5, bgcolor: 'action.hover', border: '1px solid', borderColor: 'divider' }}>
                  <Typography variant="caption" color="text.secondary" fontWeight={700}>COLUMN & CONSTRAINT</Typography>
                  <Typography variant="h6" fontWeight={800} color="primary.main" sx={{ mt: 0.5 }}>
                    {selectedDetail.column_name}
                  </Typography>
                  <Typography variant="body2" fontWeight={600} color="text.secondary">
                    {selectedDetail.constraint_name || 'No constraint name'}
                  </Typography>
                </Paper>
              </Grid>

              <Grid item xs={6}>
                <Paper variant="outlined" sx={{ p: 2, borderRadius: 1.5 }}>
                  <Typography variant="caption" color="text.secondary" fontWeight={700}>SEVERITY LEVEL</Typography>
                  <Box sx={{ mt: 0.5 }}>
                    <Chip
                      label={selectedDetail.severity_level}
                      size="small"
                      color={selectedDetail.severity_level === 'critical' ? 'error' : 'warning'}
                      variant="outlined"
                      sx={{ fontWeight: 600, textTransform: 'capitalize' }}
                    />
                  </Box>
                </Paper>
              </Grid>

              <Grid item xs={6}>
                <Paper variant="outlined" sx={{ p: 2, borderRadius: 1.5 }}>
                  <Typography variant="caption" color="text.secondary" fontWeight={700}>SOURCE</Typography>
                  <Box sx={{ mt: 0.5 }}>
                    <Chip
                      label={selectedDetail.source}
                      size="small"
                      variant="outlined"
                      sx={{ textTransform: 'capitalize', fontWeight: 600 }}
                    />
                  </Box>
                </Paper>
              </Grid>

              <Grid item xs={12}>
                <Paper variant="outlined" sx={{ p: 2, borderRadius: 1.5 }}>
                  <Typography variant="caption" color="text.secondary" fontWeight={700}>FREQUENCY</Typography>
                  <Typography variant="body1" fontWeight={700} color="primary.main" sx={{ mt: 0.5 }}>
                    {selectedDetail.frequency ?? '-'}
                  </Typography>
                </Paper>
              </Grid>

              <Grid item xs={12}>
                <Paper variant="outlined" sx={{ p: 2, borderRadius: 1.5, bgcolor: 'grey.50', fontFamily: 'monospace' }}>
                  <Typography variant="caption" color="text.secondary" fontWeight={700}>CONSTRAINT CODE</Typography>
                  <Typography variant="body2" sx={{ mt: 0.5, whiteSpace: 'pre-wrap', wordBreak: 'break-all', fontFamily: 'Courier New, monospace', fontWeight: 600, color: 'text.primary' }}>
                    {selectedDetail.code_for_constraint}
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

              <Grid item xs={6}>
                <Paper variant="outlined" sx={{ p: 2, borderRadius: 1.5 }}>
                  <Typography variant="caption" color="text.secondary" fontWeight={700}>CREATED BY</Typography>
                  <Typography variant="body2" sx={{ mt: 0.5 }}>
                    {selectedDetail.created_by_user?.full_name || selectedDetail.created_by_user?.username || 'System'}
                  </Typography>
                </Paper>
              </Grid>

              <Grid item xs={6}>
                <Paper variant="outlined" sx={{ p: 2, borderRadius: 1.5 }}>
                  <Typography variant="caption" color="text.secondary" fontWeight={700}>UPDATED BY</Typography>
                  <Typography variant="body2" sx={{ mt: 0.5 }}>
                    {selectedDetail.last_modified_by_user?.full_name || selectedDetail.last_modified_by_user?.username || 'System'}
                  </Typography>
                </Paper>
              </Grid>
            </Grid>
          ) : null}
        </DialogContent>
        <DialogActions sx={{ p: 2, justifyContent: 'space-between' }}>
          {isEditing ? (
            <>
              <Button onClick={handleCancelEdit} color="inherit">Cancel</Button>
              <Button variant="contained" onClick={handleSave}>Save</Button>
            </>
          ) : (
            <>
              <Button onClick={() => setOpenDetailDialog(false)} color="inherit">Close</Button>
              <Stack direction="row" spacing={2} alignItems="center">
                {canApproveDeactivate && selectedDetail && (
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
                )}
                {canCreateUpdate && (
                  <Button
                    variant="outlined"
                    startIcon={<Edit fontSize="small" />}
                    onClick={handleEditFromDetail}
                  >
                    Edit
                  </Button>
                )}
                {canDelete && (
                  <Button
                    variant="contained"
                    color="error"
                    startIcon={<Delete fontSize="small" />}
                    onClick={() => handleDelete(selectedDetail.id)}
                  >
                    Delete
                  </Button>
                )}
              </Stack>
            </>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Rule;
