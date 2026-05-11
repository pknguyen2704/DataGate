import React, { useState, useEffect } from "react";
import { 
  Box, Table, TableBody, TableCell, TableHead, TableRow, 
  Typography, Paper, Stack, IconButton, Button,
  Dialog, DialogTitle, DialogContent, DialogActions, TextField,
  FormControl, InputLabel, Select, MenuItem
} from "@mui/material";
import { 
  RefreshOutlined, EditOutlined, DeleteOutline, AddOutlined 
} from "@mui/icons-material";
import { metricsApi } from "~/apis/metricsApi";
import { observabilityApi } from "~/apis/observabilityApi";
import { StateBox, StatusChip, TabContainer, TabButton } from "~/components/DataGate/Page";
import { useApiResource } from "~/hooks/useApiResource";
import { toast } from "react-toastify";

const metricTabs = [
  { value: "metadata", label: "Metadata Verify" },
  { value: "profiling", label: "Profiling Verify" },
  { value: "auc", label: "Anomaly Detection" },
];

const INITIAL_FORM = {
  metric_name: "",
  column_name: "",
  min_threshold: "",
  max_threshold: "",
  auc_threshold: "",
  severity_level: "critical",
  is_active: true
};

function DataMetric() {
  const tree = useApiResource(() => observabilityApi.managedTree());
  const [selectedTableId, setSelectedTableId] = useState("");
  const [selectedTableName, setSelectedTableName] = useState("");
  const [type, setType] = useState("metadata");

  const thresholds = useApiResource(
    () => metricsApi.list(type, { table_id: selectedTableId }), 
    [type, selectedTableId]
  );

  const [openDialog, setOpenDialog] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [form, setForm] = useState(INITIAL_FORM);
  const [saving, setSaving] = useState(false);

  const allTables = React.useMemo(() => {
    if (!tree.data) return [];
    return tree.data.flatMap(schema => 
      schema.tables.map(table => ({
        ...table,
        full_name: `${schema.schema_name}.${table.table_name}`
      }))
    );
  }, [tree.data]);

  useEffect(() => {
    if (allTables.length > 0 && !selectedTableId) {
      const first = allTables[0];
      setSelectedTableId(first.table_id);
      setSelectedTableName(first.full_name);
    }
  }, [allTables, selectedTableId]);

  const handleTableChange = (e) => {
    const table = allTables.find(t => t.table_id === e.target.value);
    if (table) {
      setSelectedTableId(table.table_id);
      setSelectedTableName(table.full_name);
    }
  };

  const handleOpenAdd = () => {
    setForm(INITIAL_FORM);
    setEditingId(null);
    setOpenDialog(true);
  };

  const handleOpenEdit = (row) => {
    setForm({
      metric_name: row.metric_name || "",
      column_name: row.column_name || "",
      min_threshold: row.min_threshold ?? "",
      max_threshold: row.max_threshold ?? "",
      auc_threshold: row.auc_threshold ?? "",
      severity_level: row.severity_level || "critical",
      is_active: row.is_active ?? true
    });
    setEditingId(row.id);
    setOpenDialog(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this threshold?")) return;
    try {
      await metricsApi.delete(type, id);
      toast.success("Deleted successfully");
      thresholds.reload();
    } catch (err) {
      toast.error("Failed to delete");
    }
  };

  const handleSave = async () => {
    if (!selectedTableId) return;
    setSaving(true);
    try {
      // Remove table_id from payload if updating, as the schema doesn't expect it
      const { ...cleanForm } = form;
      
      // Convert empty strings to null for thresholds
      if (cleanForm.min_threshold === "") cleanForm.min_threshold = null;
      if (cleanForm.max_threshold === "") cleanForm.max_threshold = null;
      if (cleanForm.auc_threshold === "") cleanForm.auc_threshold = null;

      const payload = editingId ? cleanForm : { ...cleanForm, table_id: selectedTableId };
      
      if (editingId) {
        await metricsApi.update(type, editingId, payload);
        toast.success("Updated successfully");
      } else {
        await metricsApi.create(type, payload);
        toast.success("Created successfully");
      }
      setOpenDialog(false);
      thresholds.reload();
    } catch (err) {
      toast.error("Failed to save");
    } finally {
      setSaving(false);
    }
  };

  const rows = thresholds.data || [];

  return (
    <Box sx={{ p: { xs: 2, md: 3 }, bgcolor: "background.default", flexGrow: 1, overflow: "hidden" }}>
      <Stack spacing={3}>
        <Paper variant="outlined" sx={{ p: 2.5, borderRadius: 2, bgcolor: 'white', display: 'flex', justifyContent: 'space-between', alignItems: 'center', border: '1px solid', borderColor: 'divider', boxShadow: '0 2px 10px rgba(0,0,0,0.02)' }}>
          <Box>
            <Typography variant="h5" sx={{ fontWeight: 800, color: 'primary.main' }}>Data Metric & Quality</Typography>
            <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>Table-level threshold configuration and metric observability.</Typography>
          </Box>
          <Button startIcon={<RefreshOutlined />} variant="outlined" onClick={() => { tree.reload(); thresholds.reload(); }} sx={{ borderRadius: 1.5 }}>Refresh</Button>
        </Paper>

        <Paper variant="outlined" sx={{ p: 2.5, borderRadius: 2, bgcolor: 'white', border: '1px solid', borderColor: 'divider', boxShadow: '0 2px 10px rgba(0,0,0,0.02)' }}>
          <Stack direction={{ xs: 'column', md: 'row' }} spacing={3} alignItems="center">
            <FormControl size="small" sx={{ minWidth: 300, bgcolor: 'white' }}>
              <InputLabel>Table Source</InputLabel>
              <Select value={selectedTableId} label="Table Source" onChange={handleTableChange}>
                {allTables.map(t => (
                  <MenuItem key={t.table_id} value={t.table_id}>{t.full_name}</MenuItem>
                ))}
              </Select>
            </FormControl>
            <TabContainer sx={{ mb: 0, p: 0.5, bgcolor: 'grey.100' }}>
              {metricTabs.map((tabObj) => (
                <TabButton
                  key={tabObj.value}
                  active={tabObj.value === type}
                  label={tabObj.label}
                  onClick={() => setType(tabObj.value)}
                />
              ))}
            </TabContainer>
          </Stack>
        </Paper>

        <Paper variant="outlined" sx={{ borderRadius: 2, overflow: 'hidden', bgcolor: 'white', border: '1px solid', borderColor: 'divider', boxShadow: '0 4px 20px rgba(0,0,0,0.03)' }}>
          <Box sx={{ p: 2.5, borderBottom: '1px solid', borderColor: 'divider', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6" fontWeight="bold">
              {metricTabs.find((tab) => tab.value === type)?.label} Thresholds - <span style={{ color: '#1E40AF' }}>{selectedTableName}</span>
            </Typography>
            <Button variant="contained" size="small" startIcon={<AddOutlined />} onClick={handleOpenAdd} sx={{ borderRadius: 1.5 }}>
              Add Threshold
            </Button>
          </Box>
          
          <StateBox loading={thresholds.loading} error={thresholds.error} empty={!rows.length}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  {type !== "auc" ? (
                    <>
                      <TableCell sx={{ bgcolor: '#1E40AF !important', color: 'white !important', fontWeight: 'bold', py: 2 }}>Metric</TableCell>
                      <TableCell sx={{ bgcolor: '#1E40AF !important', color: 'white !important', fontWeight: 'bold', py: 2 }}>Column</TableCell>
                      <TableCell sx={{ bgcolor: '#1E40AF !important', color: 'white !important', fontWeight: 'bold', py: 2 }}>Min</TableCell>
                      <TableCell sx={{ bgcolor: '#1E40AF !important', color: 'white !important', fontWeight: 'bold', py: 2 }}>Max</TableCell>
                    </>
                  ) : (
                    <>
                      <TableCell sx={{ bgcolor: '#1E40AF !important', color: 'white !important', fontWeight: 'bold', py: 2 }}>Model ID</TableCell>
                      <TableCell sx={{ bgcolor: '#1E40AF !important', color: 'white !important', fontWeight: 'bold', py: 2 }}>AUC Threshold</TableCell>
                    </>
                  )}
                  <TableCell sx={{ bgcolor: '#1E40AF !important', color: 'white !important', fontWeight: 'bold', py: 2 }}>Severity</TableCell>
                  <TableCell sx={{ bgcolor: '#1E40AF !important', color: 'white !important', fontWeight: 'bold', py: 2 }}>Status</TableCell>
                  <TableCell align="right" sx={{ bgcolor: '#1E40AF !important', color: 'white !important', fontWeight: 'bold', py: 2 }}>Action</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {rows.map((row) => (
                  <TableRow key={row.id} hover sx={{ '&:last-child td, &:last-child th': { border: 0 } }}>
                    {type !== "auc" ? (
                      <>
                        <TableCell sx={{ fontWeight: 500 }}>{row.metric_name}</TableCell>
                        <TableCell>{row.column_name || "-"}</TableCell>
                        <TableCell>{row.min_threshold ?? "-"}</TableCell>
                        <TableCell>{row.max_threshold ?? "-"}</TableCell>
                      </>
                    ) : (
                      <>
                        <TableCell sx={{ fontWeight: 500 }}>{row.lightgbm_parameter_id || "auc_score"}</TableCell>
                        <TableCell>{row.auc_threshold ?? "-"}</TableCell>
                      </>
                    )}
                    <TableCell><StatusChip value={row.severity_level} /></TableCell>
                    <TableCell><StatusChip value={row.is_active == null ? "active" : row.is_active ? "active" : "inactive"} /></TableCell>
                    <TableCell align="right">
                      <Stack direction="row" spacing={1} justifyContent="flex-end">
                        <IconButton size="small" color="primary" onClick={() => handleOpenEdit(row)} sx={{ bgcolor: 'primary.50', '&:hover': { bgcolor: 'primary.100' } }}>
                          <EditOutlined fontSize="small" />
                        </IconButton>
                        <IconButton size="small" color="error" onClick={() => handleDelete(row.id)} sx={{ bgcolor: 'error.50', '&:hover': { bgcolor: 'error.100' } }}>
                          <DeleteOutline fontSize="small" />
                        </IconButton>
                      </Stack>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </StateBox>
        </Paper>
      </Stack>

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth PaperProps={{ sx: { borderRadius: 2 } }}>
        <DialogTitle sx={{ bgcolor: '#1E40AF', color: 'white', fontWeight: 'bold', py: 2 }}>
          {editingId ? "Edit" : "Add"} {type === 'auc' ? 'AUC' : type} Threshold
        </DialogTitle>
        <DialogContent dividers sx={{ p: 3 }}>
          <Stack spacing={3}>
            {type !== "auc" ? (
              <>
                <TextField 
                  label="Metric Name" 
                  fullWidth 
                  size="small" 
                  value={form.metric_name}
                  onChange={e => setForm({...form, metric_name: e.target.value})}
                />
                <TextField 
                  label="Column Name" 
                  fullWidth 
                  size="small" 
                  value={form.column_name}
                  onChange={e => setForm({...form, column_name: e.target.value})}
                />
                <Stack direction="row" spacing={2}>
                  <TextField 
                    label="Min Threshold" 
                    type="number" 
                    fullWidth 
                    size="small" 
                    value={form.min_threshold}
                    onChange={e => setForm({...form, min_threshold: e.target.value})}
                  />
                  <TextField 
                    label="Max Threshold" 
                    type="number" 
                    fullWidth 
                    size="small" 
                    value={form.max_threshold}
                    onChange={e => setForm({...form, max_threshold: e.target.value})}
                  />
                </Stack>
              </>
            ) : (
              <TextField 
                label="AUC Threshold" 
                type="number" 
                fullWidth 
                size="small" 
                value={form.auc_threshold}
                onChange={e => setForm({...form, auc_threshold: e.target.value})}
                helperText="Value between 0 and 1"
              />
            )}
            <FormControl fullWidth size="small">
              <InputLabel>Severity</InputLabel>
              <Select 
                value={form.severity_level} 
                label="Severity"
                onChange={e => setForm({...form, severity_level: e.target.value})}
              >
                <MenuItem value="critical">Critical</MenuItem>
                <MenuItem value="warning">Warning</MenuItem>
              </Select>
            </FormControl>
            <FormControl fullWidth size="small">
              <InputLabel>Status</InputLabel>
              <Select 
                value={form.is_active} 
                label="Status"
                onChange={e => setForm({...form, is_active: e.target.value})}
              >
                <MenuItem value={true}>Active</MenuItem>
                <MenuItem value={false}>Inactive</MenuItem>
              </Select>
            </FormControl>
          </Stack>
        </DialogContent>
        <DialogActions sx={{ p: 2.5, gap: 1 }}>
          <Button onClick={() => setOpenDialog(false)} color="inherit" sx={{ fontWeight: 'bold' }}>Cancel</Button>
          <Button variant="contained" onClick={handleSave} disabled={saving} sx={{ fontWeight: 'bold', px: 4 }}>
            {saving ? "Saving..." : editingId ? "Update" : "Create"}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default DataMetric;
