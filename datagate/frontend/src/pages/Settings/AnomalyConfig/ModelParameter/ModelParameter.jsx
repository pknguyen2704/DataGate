import React, { useState } from "react";
import {
  Box, Button, Table, TableBody, TableCell, TableHead, TableRow,
  Paper, Stack, IconButton, Dialog, DialogTitle, DialogContent,
  DialogActions, TextField, Typography, Tooltip, MenuItem, Select,
  FormControl, InputLabel, TablePagination, TableContainer, Grid, Divider
} from "@mui/material";
import {
  AddOutlined, EditOutlined, DeleteOutline,
  UploadFileOutlined, SaveOutlined,
  DescriptionOutlined, VisibilityOutlined, ArrowBackOutlined
} from "@mui/icons-material";
import { useSelector } from "react-redux";
import { modelParametersApi } from "~/apis/modelConfigsApi";
import { dataAssetsApi } from "~/apis/dataAssetsApi";

import { StateBox } from "~/components/Common/DataDisplay";
import { useApiResource } from "~/hooks/useApiResource";

import { toast } from "react-toastify";

import { useConfirm } from "material-ui-confirm";

const INITIAL_PARAMS = {
  table_id: "",
  learning_rate: 0.05,
  num_leaves: 31,
  max_depth: -1,
  min_data_in_leaf: 20,
  bagging_fraction: 0.8,
  bagging_freq: 5,
  feature_fraction: 0.8,
  lambda_l1: 0.0,
  lambda_l2: 0.0,
  min_gain_to_split: 0.0,
  max_bin: 255,
  num_iterations: 100
};

function ModelParameter() {
  const confirm = useConfirm();
  const { user } = useSelector(state => state.auth);
  const isAdmin = user?.roles?.some(r => r === "Admin" || r?.name === "Admin");
  const canUpdate = isAdmin || user?.permissions?.some(p => p === "model_config:update" || p?.code === "model_config:update");
  const canDelete = isAdmin || user?.permissions?.some(p => p === "model_config:delete" || p?.code === "model_config:delete");
  const canManage = canUpdate; // Use update as the base for manage UI elements
  
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  
  const configs = useApiResource(() => modelParametersApi.list({ 
    page: page + 1, 
    page_size: pageSize 
  }), [page, pageSize]);
  
  const tablesRes = useApiResource(() => dataAssetsApi.list({ page_size: 1000 }));
  
  const [openDialog, setOpenDialog] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [selectedId, setSelectedId] = useState(null);
  const [form, setForm] = useState(INITIAL_PARAMS);
  const [saving, setSaving] = useState(false);

  const allTables = React.useMemo(() => {
    if (!tablesRes.data || !tablesRes.data.items) return [];
    return tablesRes.data.items
      .filter(t => t.schema_name?.toLowerCase() === "silver")
      .map(t => ({
        table_id: t.id,
        table_name: t.table_name,
        schema_name: t.schema_name,
        full_name: `${t.schema_name}.${t.table_name}`
      }));
  }, [tablesRes.data]);

  const handleOpenAdd = () => {
    setForm(INITIAL_PARAMS);
    setEditingId(null);
    setOpenDialog(true);
  };

  const handleOpenEdit = (row) => {
    setForm(row);
    setEditingId(row.id);
    setOpenDialog(true);
  };

  const handleDelete = (id) => {
    confirm({
      title: "Delete Configuration",
      description: "Are you sure you want to permanently delete this configuration?",
      confirmationText: "Delete",
      cancellationText: "Cancel",
      confirmationButtonProps: { color: "error", variant: "contained" }
    })
      .then(async () => {
        try {
          await modelParametersApi.delete(id);
          toast.success("Deleted");
          if (selectedId === id) {
            setSelectedId(null);
          }
          configs.reload();
        } catch (error) {
          console.error(error);
          toast.error("Failed to delete");
        }
      })
      .catch(() => {});
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      if (editingId) {
        await modelParametersApi.update(editingId, form);
        toast.success("Updated");
      } else {
        await modelParametersApi.create(form);
        toast.success("Created");
      }
      setOpenDialog(false);
      configs.reload();
    } catch (error) {
      console.error(error);
      toast.error(error.response?.data?.detail || "Save failed");
    } finally {
      setSaving(false);
    }
  };

  const handleJsonUpload = async (e) => {
    const file = e.target.files[0];
    if (!file || !editingId && !form.table_id) {
      toast.warning("Please select a table first");
      return;
    }
    
    const reader = new FileReader();
    reader.onload = async (event) => {
      try {
        const parsed = JSON.parse(event.target.result);
        const tableId = editingId ? form.table_id : form.table_id;
        await modelParametersApi.uploadJson(tableId, parsed);
        toast.success("JSON uploaded and mapped successfully");
        setOpenDialog(false);
        configs.reload();
      } catch (error) {
        console.error(error);
        toast.error("Upload failed: " + (error.response?.data?.detail || "Invalid JSON"));
      }
    };
    reader.readAsText(file);
    e.target.value = null;
  };

  const handleDownloadTemplate = async () => {
    try {
      const res = await modelParametersApi.getTemplate();
      const blob = new Blob([JSON.stringify(res.data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      anchor.href = url;
      anchor.download = 'model_parameter_template.json';
      anchor.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error(error);
      toast.error("Failed to fetch template");
    }
  };

  let configItems = [];
  if (configs.data && configs.data.items) {
    configItems = configs.data.items;
  }
  const selectedConfig = configItems.find((item) => item.id === selectedId);

  const tableNameById = allTables.reduce((acc, table) => {
    acc[table.table_id] = table.full_name;
    return acc;
  }, {});

  const detailFields = [
    ["learning_rate", "Learning Rate"],
    ["num_leaves", "Num Leaves"],
    ["max_depth", "Max Depth"],
    ["min_data_in_leaf", "Min Data In Leaf"],
    ["bagging_fraction", "Bagging Fraction"],
    ["bagging_freq", "Bagging Freq"],
    ["feature_fraction", "Feature Fraction"],
    ["lambda_l1", "Lambda L1"],
    ["lambda_l2", "Lambda L2"],
    ["min_gain_to_split", "Min Gain To Split"],
    ["max_bin", "Max Bin"],
    ["num_iterations", "Num Iterations"],
  ];

  const parameterDialog = (
    <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
      <DialogTitle sx={{ fontWeight: 'bold' }}>
        {editingId ? "Edit" : "New"} Model parameters
      </DialogTitle>
      <DialogContent dividers>
        <Grid container spacing={2} sx={{ mt: 0.5 }}>
          <Grid item xs={12}>
            <Typography variant="subtitle2" fontWeight={700} color="text.secondary" sx={{ mb: 1 }}>SOURCE TABLE</Typography>
            <FormControl fullWidth size="small" disabled={!!editingId} sx={{ '& .MuiInputLabel-root': { fontWeight: 600 } }}>
              <InputLabel>Choose Table</InputLabel>
              <Select 
                value={form.table_id} 
                label="Choose Table"
                onChange={e => setForm({...form, table_id: e.target.value})}
                sx={{ borderRadius: 1.5 }}
              >
                {allTables.length === 0 ? (
                  <MenuItem disabled>No tables found</MenuItem>
                ) : (
                  allTables.map(t => <MenuItem key={t.table_id} value={t.table_id}>{t.full_name}</MenuItem>)
                )}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} sx={{ my: 1 }}>
            <Divider sx={{ mb: 2 }} />
            <Typography variant="subtitle2" fontWeight={700} color="text.secondary" sx={{ mb: 1 }}>Parameters value</Typography>
          </Grid>
          
          <Grid item xs={12} md={3}>
            <TextField label="Learning Rate" type="number" fullWidth size="small" value={form.learning_rate} onChange={e => setForm({...form, learning_rate: parseFloat(e.target.value)})} />
          </Grid>
          <Grid item xs={12} md={3}>
            <TextField label="Num Leaves" type="number" fullWidth size="small" value={form.num_leaves} onChange={e => setForm({...form, num_leaves: parseInt(e.target.value)})} />
          </Grid>
          <Grid item xs={12} md={3}>
            <TextField label="Max Depth" type="number" fullWidth size="small" value={form.max_depth} onChange={e => setForm({...form, max_depth: parseInt(e.target.value)})} />
          </Grid>
          <Grid item xs={12} md={3}>
            <TextField label="Min Data in Leaf" type="number" fullWidth size="small" value={form.min_data_in_leaf} onChange={e => setForm({...form, min_data_in_leaf: parseInt(e.target.value)})} />
          </Grid>
          
          <Grid item xs={12} md={3}>
            <TextField label="Bagging Fraction" type="number" fullWidth size="small" value={form.bagging_fraction} onChange={e => setForm({...form, bagging_fraction: parseFloat(e.target.value)})} />
          </Grid>
          <Grid item xs={12} md={3}>
            <TextField label="Bagging Freq" type="number" fullWidth size="small" value={form.bagging_freq} onChange={e => setForm({...form, bagging_freq: parseInt(e.target.value)})} />
          </Grid>
          <Grid item xs={12} md={3}>
            <TextField label="Feature Fraction" type="number" fullWidth size="small" value={form.feature_fraction} onChange={e => setForm({...form, feature_fraction: parseFloat(e.target.value)})} />
          </Grid>
          <Grid item xs={12} md={3}>
            <TextField label="Num Iterations" type="number" fullWidth size="small" value={form.num_iterations} onChange={e => setForm({...form, num_iterations: parseInt(e.target.value)})} />
          </Grid>

          <Grid item xs={12} md={3}>
            <TextField label="Lambda L1" type="number" fullWidth size="small" value={form.lambda_l1} onChange={e => setForm({...form, lambda_l1: parseFloat(e.target.value)})} />
          </Grid>
          <Grid item xs={12} md={3}>
            <TextField label="Lambda L2" type="number" fullWidth size="small" value={form.lambda_l2} onChange={e => setForm({...form, lambda_l2: parseFloat(e.target.value)})} />
          </Grid>
          <Grid item xs={12} md={3}>
            <TextField label="Min Gain to Split" type="number" fullWidth size="small" value={form.min_gain_to_split} onChange={e => setForm({...form, min_gain_to_split: parseFloat(e.target.value)})} />
          </Grid>
          <Grid item xs={12} md={3}>
            <TextField label="Max Bin" type="number" fullWidth size="small" value={form.max_bin} onChange={e => setForm({...form, max_bin: parseInt(e.target.value)})} />
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions sx={{ p: 2, justifyContent: 'space-between' }}>
        <Stack direction="row" spacing={1}>
          <Button startIcon={<DescriptionOutlined />} onClick={handleDownloadTemplate}>
            Download Template
          </Button>
          <Button component="label" startIcon={<UploadFileOutlined />} disabled={!form.table_id}>
            Upload JSON
            <input type="file" accept=".json" hidden onChange={handleJsonUpload} />
          </Button>
        </Stack>
        <Stack direction="row" spacing={1}>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button variant="contained" startIcon={<SaveOutlined />} onClick={handleSave} disabled={saving || !form.table_id}>
            {saving ? "Saving..." : "Save Config"}
          </Button>
        </Stack>
      </DialogActions>
    </Dialog>
  );

  if (selectedConfig) {
    return (
      <Box sx={{ p: 0, pt: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <IconButton onClick={() => setSelectedId(null)} sx={{ mr: 1 }} color="primary">
            <ArrowBackOutlined />
          </IconButton>
          <Typography variant="h6" fontWeight={700}>Parameter Details</Typography>
        </Box>

        <Paper variant="outlined" sx={{ p: 3, borderRadius: 2 }}>
          <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 3, pb: 2, borderBottom: 1, borderColor: 'divider' }}>
            <Box>
              <Typography variant="caption" color="text.secondary" fontWeight={700}>SOURCE TABLE</Typography>
              <Typography variant="h6" fontWeight={800}>
                {tableNameById[selectedConfig.table_id] || selectedConfig.table_id.substring(0, 8)}
              </Typography>
            </Box>
            <Stack direction="row" spacing={1}>
              {canManage && (
                <Button size="small" variant="outlined" startIcon={<EditOutlined />} onClick={() => handleOpenEdit(selectedConfig)}>
                  Edit
                </Button>
              )}
              {canDelete && (
                <Button size="small" variant="outlined" color="error" startIcon={<DeleteOutline />} onClick={() => handleDelete(selectedConfig.id)}>
                  Delete
                </Button>
              )}
            </Stack>
          </Stack>

          <Grid container spacing={3}>
            {detailFields.map(([field, label]) => (
              <Grid item xs={12} sm={6} md={3} key={field}>
                <Paper variant="outlined" sx={{ p: 2, borderRadius: 1.5, bgcolor: 'action.hover' }}>
                  <Typography variant="caption" color="text.secondary" fontWeight={700}>{label}</Typography>
                  <Typography variant="body1" fontWeight={600} sx={{ overflowWrap: 'anywhere', mt: 0.5 }}>
                    {selectedConfig[field]}
                  </Typography>
                </Paper>
              </Grid>
            ))}
          </Grid>
        </Paper>

        {parameterDialog}
      </Box>
    );
  }

  return (
    <Box sx={{ p: 0, pt: 1 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3, alignItems: 'center' }}>
        <Box>
          <Typography variant="h5" fontWeight={800} color="primary">Model parameters</Typography>
          <Typography variant="body2" color="text.secondary">Configure LightGBM training hyperparameters for silver tables.</Typography>
        </Box>
        <Stack direction="row" spacing={1}>
          {canManage && (
            <Button startIcon={<AddOutlined />} variant="contained" onClick={handleOpenAdd}>
              New parameters
            </Button>
          )}
        </Stack>
      </Box>

      <StateBox loading={configs.loading} error={configs.error} empty={configItems.length === 0}>
        <TableContainer component={Paper} variant="outlined" sx={{ borderRadius: 2, overflow: 'hidden' }}>
          <Table size="small">
            <TableHead>
              <TableRow sx={{ bgcolor: 'primary.main' }}>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Source Table</TableCell>
                <TableCell align="right" sx={{ color: 'white', fontWeight: 'bold' }}>Iterations</TableCell>
                <TableCell align="right" sx={{ color: 'white', fontWeight: 'bold' }}>Learning Rate</TableCell>
                <TableCell align="right" sx={{ color: 'white', fontWeight: 'bold' }}>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {configItems.map((row) => (
                <TableRow
                  key={row.id}
                  hover
                  onClick={() => setSelectedId(row.id)}
                  sx={{ cursor: 'pointer' }}
                >
                  <TableCell sx={{ fontWeight: 600, whiteSpace: 'nowrap' }}>
                    {tableNameById[row.table_id] || row.table_id.substring(0, 8)}
                  </TableCell>
                  <TableCell align="right">{row.num_iterations}</TableCell>
                  <TableCell align="right">{row.learning_rate}</TableCell>
                  <TableCell align="right">
                    <Tooltip title="View details">
                      <IconButton size="small" color="primary" onClick={(e) => { e.stopPropagation(); setSelectedId(row.id); }}>
                        <VisibilityOutlined fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          <TablePagination
            rowsPerPageOptions={[5, 10, 25]}
            component="div"
            count={configs.data?.total || 0}
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

      {parameterDialog}
    </Box>
  );
}

export default ModelParameter;
