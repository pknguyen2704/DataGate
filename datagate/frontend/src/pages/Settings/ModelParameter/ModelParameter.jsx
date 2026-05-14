import React, { useState } from "react";
import { 
  Box, Button, Table, TableBody, TableCell, TableHead, TableRow, 
  Paper, Stack, IconButton, Dialog, DialogTitle, DialogContent, 
  DialogActions, TextField, Typography, Tooltip, MenuItem, Select,
  FormControl, InputLabel, TablePagination, TableContainer, Grid, Divider, Switch, Chip
} from "@mui/material";
import { 
  RefreshOutlined, AddOutlined, EditOutlined, DeleteOutline, 
  UploadFileOutlined, DownloadOutlined, SaveOutlined,
  DescriptionOutlined
} from "@mui/icons-material";
import { useSelector } from "react-redux";
import { modelParametersApi } from "~/apis/modelConfigsApi";
import { dataAssetsApi } from "~/apis/dataAssetsApi";
import { observabilityApi } from "~/apis/observabilityApi";
import { StateBox } from "~/components/DataGate/Page";
import { useApiResource } from "~/hooks/useApiResource";
import { format } from "date-fns";
import { toast } from "react-toastify";

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
  const { user } = useSelector(state => state.auth);
  const isAdmin = user?.roles?.some(r => r === "Admin" || r?.name === "Admin");
  const hasPerm = user?.permissions?.some(p => p === "model_config:manage" || p?.code === "model_config:manage");
  const canManage = isAdmin || hasPerm;
  
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  
  const configs = useApiResource(() => modelParametersApi.list({ 
    page: page + 1, 
    page_size: pageSize 
  }), [page, pageSize]);
  
  const tablesRes = useApiResource(() => dataAssetsApi.list({ page_size: 1000 }));
  
  const [openDialog, setOpenDialog] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [form, setForm] = useState(INITIAL_PARAMS);
  const [saving, setSaving] = useState(false);
  
  const [openTemplate, setOpenTemplate] = useState(false);
  const [templateJson, setTemplateJson] = useState("");

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

  const handleDelete = async (id) => {
    if (!window.confirm("Delete this configuration?")) return;
    try {
      await modelParametersApi.delete(id);
      toast.success("Deleted");
      configs.reload();
    } catch (err) {
      toast.error("Failed to delete");
    }
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
    } catch (err) {
      toast.error(err.response?.data?.detail || "Save failed");
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
      } catch (err) {
        toast.error("Upload failed: " + (err.response?.data?.detail || "Invalid JSON"));
      }
    };
    reader.readAsText(file);
    e.target.value = null;
  };

  const handleShowTemplate = async () => {
    try {
      const res = await modelParametersApi.getTemplate();
      setTemplateJson(JSON.stringify(res.data, null, 2));
      setOpenTemplate(true);
    } catch (err) {
      toast.error("Failed to fetch template");
    }
  };

  let configItems = [];
  if (configs.data && configs.data.items) {
    configItems = configs.data.items;
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3, alignItems: 'center' }}>
        <Typography variant="h5" fontWeight={800} color="primary">Model parameters</Typography>
        <Stack direction="row" spacing={1}>
          <Button startIcon={<DescriptionOutlined />} variant="outlined" onClick={handleShowTemplate}>
            Template
          </Button>
          <Button startIcon={<RefreshOutlined />} variant="outlined" onClick={configs.reload}>
            Refresh
          </Button>
          {canManage && (
            <Button startIcon={<AddOutlined />} variant="contained" onClick={handleOpenAdd}>
              New parameters
            </Button>
          )}
        </Stack>
      </Box>

      <StateBox loading={configs.loading} error={configs.error} empty={configItems.length === 0}>
        <TableContainer component={Paper} variant="outlined" sx={{ borderRadius: 2 }}>
          <Table size="small">
            <TableHead>
              <TableRow sx={{ bgcolor: 'primary.main' }}>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Source Table</TableCell>
                <TableCell align="right" sx={{ color: 'white', fontWeight: 'bold' }}>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {configItems.map((row) => (
                <TableRow key={row.id} hover>
                  <TableCell sx={{ fontWeight: 600, whiteSpace: 'nowrap' }}>
                    {allTables.find(t => t.table_id === row.table_id)?.full_name || row.table_id.substring(0, 8)}
                  </TableCell>
                  <TableCell align="right">
                    <Stack direction="row" spacing={0.5} justifyContent="flex-end">
                      <Tooltip title="Edit">
                        <IconButton size="small" color="primary" onClick={() => handleOpenEdit(row)}>
                          <EditOutlined fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      {isAdmin && (
                        <Tooltip title="Delete">
                          <IconButton size="small" color="error" onClick={() => handleDelete(row.id)}>
                            <DeleteOutline fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      )}
                    </Stack>
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

      {/* Edit/Create Dialog */}
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
          <Box>
            <Button component="label" startIcon={<UploadFileOutlined />} disabled={!form.table_id}>
              Upload JSON
              <input type="file" accept=".json" hidden onChange={handleJsonUpload} />
            </Button>
          </Box>
          <Stack direction="row" spacing={1}>
            <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
            <Button variant="contained" startIcon={<SaveOutlined />} onClick={handleSave} disabled={saving || !form.table_id}>
              {saving ? "Saving..." : "Save Config"}
            </Button>
          </Stack>
        </DialogActions>
      </Dialog>

      {/* Template Dialog */}
      <Dialog open={openTemplate} onClose={() => setOpenTemplate(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ fontWeight: 700 }}>JSON Template</DialogTitle>
        <DialogContent dividers>
          <Typography variant="caption" color="text.secondary" gutterBottom>
            Copy this structure and upload it to map parameters automatically.
          </Typography>
          <Box sx={{ p: 2, bgcolor: '#f1f5f9', borderRadius: 1, mt: 1 }}>
            <pre style={{ margin: 0, fontSize: '0.8rem' }}>{templateJson}</pre>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenTemplate(false)}>Close</Button>
          <Button variant="contained" startIcon={<DownloadOutlined />} onClick={() => {
            const blob = new Blob([templateJson], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'model_config_template.json';
            a.click();
          }}>Download</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default ModelParameter;