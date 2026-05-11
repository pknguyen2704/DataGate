import React, { useState, useEffect } from "react";
import { 
  Box, Button, Table, TableBody, TableCell, TableHead, TableRow, 
  Typography, Paper, Stack, IconButton,
  Dialog, DialogTitle, DialogContent, DialogActions, TextField,
  FormControl, InputLabel, Select, MenuItem
} from "@mui/material";
import { 
  RefreshOutlined, EditOutlined, DeleteOutline, AddOutlined, 
  PlayCircleOutline, StopCircleOutlined 
} from "@mui/icons-material";
import { rulesApi } from "~/apis/rulesApi";
import { observabilityApi } from "~/apis/observabilityApi";
import { StateBox, StatusChip } from "~/components/DataGate/Page";
import { useApiResource } from "~/hooks/useApiResource";
import { toast } from "react-toastify";

const INITIAL_FORM = {
  column_name: "",
  constraint_name: "",
  description: "",
  severity_level: "critical",
  status: "active"
};

function DataRule() {
  const managedTables = useApiResource(() => rulesApi.managedTables());
  const [selectedTableId, setSelectedTableId] = useState("");
  const [selectedTableName, setSelectedTableName] = useState("");
  const [openDialog, setOpenDialog] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [saving, setSaving] = useState(false);
  
  const [form, setForm] = useState({
    table_id: "",
    column_name: "",
    constraint_name: "",
    severity_level: "warning",
    status: "pending",
    frequency: 1,
    code_for_constraint: "",
    description: ""
  });

  const allTables = managedTables.data || [];

  useEffect(() => {
    if (allTables.length > 0 && !selectedTableId) {
      setSelectedTableId(allTables[0].id);
      setSelectedTableName(`${allTables[0].schema_name}.${allTables[0].table_name}`);
    }
  }, [allTables]);

  const rules = useApiResource(() => {
    if (selectedTableId) {
      return rulesApi.list({ table_id: selectedTableId });
    }
    return Promise.resolve({ data: [] });
  }, [selectedTableId]);

  const handleTableChange = (e) => {
    const table = allTables.find(t => t.id === e.target.value);
    if (table) {
      setSelectedTableId(table.id);
      setSelectedTableName(`${table.schema_name}.${table.table_name}`);
    }
  };

  const handleOpenAdd = () => {
    setEditingId(null);
    setForm({
      table_id: selectedTableId,
      column_name: "",
      constraint_name: "",
      severity_level: "warning",
      status: "pending",
      frequency: 1,
      code_for_constraint: "",
      description: ""
    });
    setOpenDialog(true);
  };

  const handleOpenEdit = (row) => {
    setEditingId(row.id);
    setForm({ ...row });
    setOpenDialog(true);
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      if (editingId) {
        await rulesApi.update(editingId, form);
        toast.success("Rule updated");
      } else {
        await rulesApi.create(form);
        toast.success("Rule created");
      }
      setOpenDialog(false);
      rules.reload();
    } catch (err) {
      toast.error("Failed to save rule");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure?")) return;
    try {
      await rulesApi.delete(id);
      toast.success("Rule deleted");
      rules.reload();
    } catch (err) {
      toast.error("Failed to delete rule");
    }
  };

  const rows = rules.data || [];

  return (
    <Box sx={{ p: { xs: 2, md: 3 }, bgcolor: "background.default", flexGrow: 1, overflow: "hidden" }}>
      <Stack spacing={3}>
        <Paper variant="outlined" sx={{ p: 2.5, borderRadius: 2, bgcolor: 'white', display: 'flex', justifyContent: 'space-between', alignItems: 'center', border: '1px solid', borderColor: 'divider', boxShadow: '0 2px 10px rgba(0,0,0,0.02)' }}>
          <Box>
            <Typography variant="h5" sx={{ fontWeight: 800, color: 'primary.main' }}>Data Rules Management</Typography>
            <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>Configure and manage validation rules for specific tables and columns.</Typography>
          </Box>
          <Button startIcon={<RefreshOutlined />} variant="outlined" onClick={() => { managedTables.reload(); rules.reload(); }} sx={{ borderRadius: 1.5 }}>Refresh</Button>
        </Paper>

        <Paper variant="outlined" sx={{ p: 2.5, borderRadius: 2, bgcolor: 'white', border: '1px solid', borderColor: 'divider', boxShadow: '0 2px 10px rgba(0,0,0,0.02)' }}>
          <Stack direction={{ xs: 'column', md: 'row' }} spacing={3} alignItems="center">
            <FormControl size="small" sx={{ minWidth: 350, bgcolor: 'white' }}>
              <InputLabel>Target Table (Tables with Rules)</InputLabel>
              <Select value={selectedTableId} label="Target Table (Tables with Rules)" onChange={handleTableChange}>
                {allTables.map(t => (
                  <MenuItem key={t.id} value={t.id}>{t.schema_name}.{t.table_name}</MenuItem>
                ))}
              </Select>
            </FormControl>
            <Typography variant="body2" color="text.secondary">
              Only tables with existing rules are shown here.
            </Typography>
          </Stack>
        </Paper>

        <Paper variant="outlined" sx={{ borderRadius: 2, overflow: 'hidden', bgcolor: 'white', border: '1px solid', borderColor: 'divider', boxShadow: '0 4px 20px rgba(0,0,0,0.03)' }}>
          <Box sx={{ p: 2.5, borderBottom: '1px solid', borderColor: 'divider', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6" fontWeight="bold">
              Rules Configuration - <span style={{ color: '#1E40AF' }}>{selectedTableName || "..."}</span>
            </Typography>
            <Button variant="contained" size="small" startIcon={<AddOutlined />} onClick={handleOpenAdd} sx={{ borderRadius: 1.5 }}>
              Add New Rule
            </Button>
          </Box>
          
          <StateBox loading={rules.loading || managedTables.loading} error={rules.error} empty={!rows.length}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell sx={{ bgcolor: '#1E40AF !important', color: 'white !important', fontWeight: 'bold', py: 2 }}>Column</TableCell>
                  <TableCell sx={{ bgcolor: '#1E40AF !important', color: 'white !important', fontWeight: 'bold', py: 2 }}>Constraint</TableCell>
                  <TableCell sx={{ bgcolor: '#1E40AF !important', color: 'white !important', fontWeight: 'bold', py: 2 }}>Severity</TableCell>
                  <TableCell sx={{ bgcolor: '#1E40AF !important', color: 'white !important', fontWeight: 'bold', py: 2 }}>Status</TableCell>
                  <TableCell sx={{ bgcolor: '#1E40AF !important', color: 'white !important', fontWeight: 'bold', py: 2 }}>Frequency</TableCell>
                  <TableCell align="right" sx={{ bgcolor: '#1E40AF !important', color: 'white !important', fontWeight: 'bold', py: 2 }}>Action</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {rows.map((row) => (
                  <TableRow key={row.id} hover sx={{ '&:last-child td, &:last-child th': { border: 0 } }}>
                    <TableCell sx={{ fontWeight: 600 }}>{row.column_name}</TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{ fontFamily: 'monospace', bgcolor: 'grey.100', p: 0.5, borderRadius: 1, display: 'inline-block' }}>
                        {row.constraint_name}
                      </Typography>
                    </TableCell>
                    <TableCell><StatusChip value={row.severity_level} /></TableCell>
                    <TableCell>
                      {row.status === 'pending' ? (
                        <StatusChip value="pending" sx={{ bgcolor: 'info.light', color: 'info.contrastText' }} />
                      ) : (
                        <StatusChip value={row.status} />
                      )}
                    </TableCell>
                    <TableCell>{row.frequency} batch(es)</TableCell>
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
          {editingId ? "Edit" : "Create"} Data Rule
        </DialogTitle>
        <DialogContent dividers sx={{ p: 3 }}>
          <Stack spacing={3}>
            <TextField 
              label="Column Name" 
              fullWidth 
              size="small" 
              value={form.column_name}
              onChange={e => setForm({...form, column_name: e.target.value})}
            />
            <TextField 
              label="Constraint Name" 
              fullWidth 
              size="small" 
              value={form.constraint_name}
              onChange={e => setForm({...form, constraint_name: e.target.value})}
            />
            <TextField 
              label="SQL Condition / Logic" 
              fullWidth 
              size="small" 
              multiline
              rows={3}
              value={form.code_for_constraint}
              onChange={e => setForm({...form, code_for_constraint: e.target.value})}
              helperText="Expression must return boolean (e.g. col_name > 0)"
            />
            <Stack direction="row" spacing={2}>
              <FormControl fullWidth size="small">
                <InputLabel>Severity</InputLabel>
                <Select value={form.severity_level} label="Severity" onChange={e => setForm({...form, severity_level: e.target.value})}>
                  <MenuItem value="critical">Critical</MenuItem>
                  <MenuItem value="warning">Warning</MenuItem>
                </Select>
              </FormControl>
              <FormControl fullWidth size="small">
                <InputLabel>Initial Status</InputLabel>
                <Select value={form.status} label="Initial Status" onChange={e => setForm({...form, status: e.target.value})}>
                  <MenuItem value="pending">Pending</MenuItem>
                  <MenuItem value="active">Active</MenuItem>
                  <MenuItem value="inactive">Inactive</MenuItem>
                </Select>
              </FormControl>
            </Stack>
            <TextField 
              label="Frequency (check every N batches)" 
              type="number" 
              fullWidth 
              size="small" 
              value={form.frequency}
              onChange={e => setForm({...form, frequency: parseInt(e.target.value) || 1})}
            />
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

export default DataRule;
