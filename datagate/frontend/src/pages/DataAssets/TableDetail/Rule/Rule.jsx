import React, { useState, useEffect } from "react";
import { 
  Box, Typography, Paper, Table, TableBody, TableCell, 
  TableHead, TableRow, TableContainer, Button, IconButton, 
  Chip, Dialog, DialogTitle, DialogContent, 
  DialogActions, TextField, MenuItem, Grid, Stack,
  Tooltip, Alert, FormControl, InputLabel, Select, TablePagination, Switch
} from "@mui/material";
import { 
  Add, Edit, Delete, Refresh, InfoOutlined, 
  CheckCircle, DoNotDisturb, HourglassEmpty, Search, FilterList
} from "@mui/icons-material";
import { useParams } from "react-router-dom";
import { rulesApi } from "~/apis/rulesApi";
import { useApiResource } from "~/hooks/useApiResource";
import { useSelector } from "react-redux";
import { format } from "date-fns";
import { StateBox } from "~/components/DataGate/Page";

const STATUS_COLORS = {
  active: "success",
  inactive: "default"
};

const SEVERITY_COLORS = {
  warning: "warning",
  critical: "error"
};

const Rule = () => {
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
  const [openDialog, setOpenDialog] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({});

  // Permissions
  const isAdmin = user?.roles?.some(r => r === "Admin" || r?.name === "Admin");
  
  const canSuggest = isAdmin || user?.permissions?.some(p => p === "rule:suggest" || p?.code === "rule:suggest");
  const canCreateUpdate = canSuggest;

  const canManage = isAdmin || user?.permissions?.some(p => p === "rule:manage" || p?.code === "rule:manage");
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

  const handleOpenDialog = (item = null) => {
    setEditingId(item?.id || null);
    if (item) {
      setFormData({ ...item });
    } else {
      setFormData({ 
        table_id: tableId,
        column_name: "",
        constraint_name: "",
        source: "manual",
        severity_level: "warning",
        status: "inactive",
        code_for_constraint: "",
        description: ""
      });
    }
    setOpenDialog(true);
  };

  const handleSave = async () => {
    try {
      if (editingId) {
        await rulesApi.update(editingId, formData);
      } else {
        await rulesApi.create(formData);
      }
      setOpenDialog(false);
      rulesRes.reload();
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to save rule");
    }
  };

  const handleApprove = async (id) => {
    try {
      await rulesApi.approve(id);
      rulesRes.reload();
    } catch (err) {
      alert("Approve failed");
    }
  };

  const handleDeactivate = async (id) => {
    try {
      await rulesApi.deactivate(id);
      rulesRes.reload();
    } catch (err) {
      alert("Deactivate failed");
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to permanently delete this rule?")) return;
    try {
      await rulesApi.delete(id);
      rulesRes.reload();
    } catch (err) {
      alert("Delete failed");
    }
  };

  const handleToggleActive = async (rule) => {
    try {
      if (rule.is_active) {
        await rulesApi.deactivate(rule.id);
      } else {
        await rulesApi.approve(rule.id);
      }
      rulesRes.reload();
    } catch (err) {
      alert("Toggle status failed");
    }
  };

  const getRuleStatus = (rule) => {
    return rule.is_active ? "active" : "inactive";
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header & Main Actions */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h6" fontWeight={700}>Data Quality Rules</Typography>
        <Stack direction="row" spacing={1}>
          <Button startIcon={<Refresh />} size="small" onClick={() => rulesRes.reload()}>Refresh</Button>
          {canCreateUpdate && (
            <Button variant="contained" startIcon={<Add />} onClick={() => handleOpenDialog()}>Add Rule</Button>
          )}
        </Stack>
      </Box>

      {/* Filter Bar */}
      <Paper variant="outlined" sx={{ p: 2, mb: 3, borderRadius: 2, bgcolor: 'background.default' }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={4}>
            <TextField 
              fullWidth size="small" placeholder="Search by column, constraint, description..."
              value={filters.search} onChange={(e) => handleFilterChange("search", e.target.value)}
              InputProps={{
                startAdornment: <Search fontSize="small" sx={{ mr: 1, color: 'text.secondary' }} />,
              }}
            />
          </Grid>
          <Grid item xs={12} md={2}>
            <FormControl fullWidth size="small">
              <InputLabel>Source</InputLabel>
              <Select value={filters.source} label="Source" onChange={(e) => handleFilterChange("source", e.target.value)}>
                <MenuItem value="">All Sources</MenuItem>
                <MenuItem value="manual">Manual</MenuItem>
                <MenuItem value="system">System</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={2}>
            <FormControl fullWidth size="small">
              <InputLabel>Status</InputLabel>
              <Select value={filters.rule_status} label="Status" onChange={(e) => handleFilterChange("rule_status", e.target.value)}>
                <MenuItem value="">All Status</MenuItem>
                <MenuItem value="active">Active Only</MenuItem>
                <MenuItem value="inactive">Inactive Only</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={2}>
            <FormControl fullWidth size="small">
              <InputLabel>Severity</InputLabel>
              <Select value={filters.severity_level} label="Severity" onChange={(e) => handleFilterChange("severity_level", e.target.value)}>
                <MenuItem value="">All Severities</MenuItem>
                <MenuItem value="warning">Warning</MenuItem>
                <MenuItem value="critical">Critical</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={2}>
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
        <TableContainer component={Paper} variant="outlined" sx={{ borderRadius: 2 }}>
          <Table size="small">
            <TableHead>
              <TableRow sx={{ bgcolor: 'primary.main' }}>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Column</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Constraint / Description</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Source</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Severity</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Freq</TableCell>
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
                      <Tooltip title={rule.description || rule.code_for_constraint}>
                        <Box>
                          <Typography variant="body2" fontWeight={500} sx={{ maxWidth: 250, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                            {rule.constraint_name || rule.code_for_constraint}
                          </Typography>
                          {rule.description && (
                            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', maxWidth: 250, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                              {rule.description}
                            </Typography>
                          )}
                        </Box>
                      </Tooltip>
                    </TableCell>
                    <TableCell>
                      <Chip label={rule.source} size="small" variant="outlined" sx={{ textTransform: 'capitalize', height: 20, fontSize: '0.7rem' }} />
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={rule.severity_level} 
                        size="small" 
                        color={rule.severity_level === 'critical' ? 'error' : 'warning'} 
                        variant="filled"
                        sx={{ fontWeight: 700, textTransform: 'capitalize', height: 20, fontSize: '0.65rem' }}
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" fontWeight={700} color="primary.main">{rule.frequency}</Typography>
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
                        <Typography variant="caption" sx={{ ml: 0.5, fontWeight: 600, color: rule.is_active ? 'success.main' : 'text.disabled' }}>
                          {rule.is_active ? "Active" : "Inactive"}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell align="right">
                      <Stack direction="row" spacing={0.5} justifyContent="flex-end">
                        {canCreateUpdate && (
                          <IconButton size="small" color="primary" onClick={() => handleOpenDialog(rule)}>
                            <Edit fontSize="small" />
                          </IconButton>
                        )}
                        {canDelete && (
                          <IconButton size="small" color="error" onClick={() => handleDelete(rule.id)}>
                            <Delete fontSize="small" />
                          </IconButton>
                        )}
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

      {/* Form Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{editingId ? "Edit Data Rule" : "Create Data Rule"}</DialogTitle>
        <DialogContent dividers>
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
            <Grid item xs={12} md={6}>
              <TextField
                select fullWidth label="Severity"
                value={formData.severity_level || 'warning'} onChange={(e) => setFormData({...formData, severity_level: e.target.value})}
              >
                <MenuItem value="warning">Warning</MenuItem>
                <MenuItem value="critical">Critical</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12}>
              <TextField 
                fullWidth multiline rows={3} label="Rule Description"
                value={formData.rule_description || ''} onChange={(e) => setFormData({...formData, rule_description: e.target.value})}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleSave}>Save</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Rule;