import React, { useMemo, useState } from "react";
import {
  Box,
  Button,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Divider,
  FormControl,
  Grid,
  IconButton,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TablePagination,
  TableRow,
  TextField,
  Tooltip,
  Typography,
} from "@mui/material";
import {
  AddOutlined,
  DeleteOutline,
  DescriptionOutlined,
  VisibilityOutlined,
  EditOutlined,
  SaveOutlined,
  UploadFileOutlined,
  ArrowBackOutlined,
} from "@mui/icons-material";
import { useSelector } from "react-redux";
import { toast } from "react-toastify";
import { anomalyJobConfigsApi } from "~/apis/modelConfigsApi";
import { dataAssetsApi } from "~/apis/dataAssetsApi";
import { StateBox } from "~/components/Common/DataDisplay";
import { useApiResource } from "~/hooks/useApiResource";
import { useConfirm } from "material-ui-confirm";

const INITIAL_CONFIG = {
  table_id: "",
  batch_time_col: "",
  required_history_days: 30,
  previous_batch_hours: 24,
  history_days: [7, 14, 30],
  target_sample_per_group: 10000,
  test_size: 0.2,
  random_state: 42,
  exclude_cols: [],
  categorical_cols: [],
  numeric_cols: [],
  description: "",
};

const listToText = (value) => (Array.isArray(value) ? value.join(", ") : value || "");

const parseTextList = (value) =>
  String(value || "")
    .split(/[\n,]/)
    .map((item) => item.trim())
    .filter(Boolean);

const parseNumberList = (value) =>
  parseTextList(value)
    .map((item) => Number(item))
    .filter((item) => Number.isFinite(item));

const toNumber = (value, fallback = 0) => {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
};

function Config() {
  const confirm = useConfirm();
  const { user } = useSelector((state) => state.auth);
  const isAdmin = user?.roles?.some((role) => role === "Admin" || role?.name === "Admin");
  const canUpdate =
    isAdmin ||
    user?.permissions?.some((permission) => permission === "model_config:update" || permission?.code === "model_config:update");
  const canDelete =
    isAdmin ||
    user?.permissions?.some((permission) => permission === "model_config:delete" || permission?.code === "model_config:delete");

  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [selectedId, setSelectedId] = useState(null);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState(INITIAL_CONFIG);

  const configs = useApiResource(
    () =>
      anomalyJobConfigsApi.list({
        page: page + 1,
        page_size: pageSize,
      }),
    [page, pageSize],
  );
  const tablesRes = useApiResource(() => dataAssetsApi.list({ page_size: 1000 }));

  const allTables = useMemo(() => {
    if (!tablesRes.data?.items) return [];
    return tablesRes.data.items
      .filter((table) => table.schema_name?.toLowerCase() === "silver")
      .map((table) => ({
        table_id: table.id,
        table_name: table.table_name,
        schema_name: table.schema_name,
        full_name: `${table.schema_name}.${table.table_name}`,
      }));
  }, [tablesRes.data]);

  const tableNameById = useMemo(() => {
    return allTables.reduce((acc, table) => {
      acc[table.table_id] = table.full_name;
      return acc;
    }, {});
  }, [allTables]);

  const configItems = configs.data?.items || [];
  const selectedConfig = configItems.find((item) => item.id === selectedId);

  const handleOpenAdd = () => {
    setForm(INITIAL_CONFIG);
    setEditingId(null);
    setOpenDialog(true);
  };

  const handleOpenEdit = (row) => {
    setForm({
      ...row,
      description: row.description || "",
    });
    setEditingId(row.id);
    setOpenDialog(true);
  };

  const handleDelete = (id) => {
    confirm({
      title: "Delete Configuration",
      description: "Are you sure you want to delete this anomaly job configuration?",
      confirmationText: "Delete",
      cancellationText: "Cancel",
      confirmationButtonProps: { color: "error", variant: "contained" }
    })
      .then(async () => {
        try {
          await anomalyJobConfigsApi.delete(id);
          toast.success("Deleted");
          if (selectedId === id) {
            setSelectedId(null);
          }
          configs.reload();
        } catch (err) {
          toast.error(err.response?.data?.detail || "Failed to delete");
        }
      })
      .catch(() => {});
  };

  const buildPayload = () => ({
    table_id: form.table_id,
    batch_time_col: form.batch_time_col.trim(),
    required_history_days: toNumber(form.required_history_days),
    previous_batch_hours: toNumber(form.previous_batch_hours),
    history_days: Array.isArray(form.history_days) ? form.history_days : parseNumberList(form.history_days),
    target_sample_per_group: toNumber(form.target_sample_per_group),
    test_size: toNumber(form.test_size),
    random_state: toNumber(form.random_state),
    exclude_cols: Array.isArray(form.exclude_cols) ? form.exclude_cols : parseTextList(form.exclude_cols),
    categorical_cols: Array.isArray(form.categorical_cols) ? form.categorical_cols : parseTextList(form.categorical_cols),
    numeric_cols: Array.isArray(form.numeric_cols) ? form.numeric_cols : parseTextList(form.numeric_cols),
    description: form.description?.trim() || null,
  });

  const handleSave = async () => {
    const payload = buildPayload();
    if (!payload.table_id || !payload.batch_time_col || payload.history_days.length === 0) {
      toast.warning("Please fill table, batch time column, and history days");
      return;
    }

    setSaving(true);
    try {
      if (editingId) {
        const updatePayload = { ...payload };
        delete updatePayload.table_id;
        await anomalyJobConfigsApi.update(editingId, updatePayload);
        toast.success("Updated");
      } else {
        await anomalyJobConfigsApi.create(payload);
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

  const handleDownloadTemplate = async () => {
    try {
      const res = await anomalyJobConfigsApi.getTemplate();
      const blob = new Blob([JSON.stringify(res.data, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = "anomaly_job_config_template.json";
      anchor.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to fetch template");
    }
  };

  const handleJsonUpload = async (event) => {
    const file = event.target.files[0];
    if (!file || !form.table_id) {
      toast.warning("Please select a table first");
      event.target.value = null;
      return;
    }

    const reader = new FileReader();
    reader.onload = async (readerEvent) => {
      try {
        const parsed = JSON.parse(readerEvent.target.result);
        await anomalyJobConfigsApi.uploadJson(form.table_id, parsed);
        toast.success("JSON uploaded and mapped successfully");
        setOpenDialog(false);
        configs.reload();
      } catch (err) {
        toast.error("Upload failed: " + (err.response?.data?.detail || "Invalid JSON"));
      }
    };
    reader.readAsText(file);
    event.target.value = null;
  };

  const setListField = (field, value) => {
    setForm((current) => ({ ...current, [field]: value }));
  };

  const configDialog = (
    <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
      <DialogTitle sx={{ fontWeight: "bold" }}>{editingId ? "Edit" : "New"} anomaly job config</DialogTitle>
      <DialogContent dividers>
        <Grid container spacing={2} sx={{ mt: 0.5 }}>
          <Grid item xs={12}>
            <Typography variant="subtitle2" fontWeight={700} color="text.secondary" sx={{ mb: 1 }}>
              SOURCE TABLE
            </Typography>
            <FormControl fullWidth size="small" disabled={!!editingId}>
              <InputLabel>Choose Table</InputLabel>
              <Select
                value={form.table_id}
                label="Choose Table"
                onChange={(event) => setForm({ ...form, table_id: event.target.value })}
                sx={{ borderRadius: 1.5 }}
              >
                {allTables.length === 0 ? (
                  <MenuItem disabled>No silver tables found</MenuItem>
                ) : (
                  allTables.map((table) => (
                    <MenuItem key={table.table_id} value={table.table_id}>
                      {table.full_name}
                    </MenuItem>
                  ))
                )}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} sx={{ my: 1 }}>
            <Divider sx={{ mb: 2 }} />
            <Typography variant="subtitle2" fontWeight={700} color="text.secondary">
              EXECUTION WINDOW
            </Typography>
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              label="Batch Time Column"
              fullWidth
              size="small"
              value={form.batch_time_col}
              onChange={(event) => setForm({ ...form, batch_time_col: event.target.value })}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <TextField
              label="Required History Days"
              type="number"
              fullWidth
              size="small"
              value={form.required_history_days}
              onChange={(event) => setForm({ ...form, required_history_days: event.target.value })}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <TextField
              label="Previous Batch Hours"
              type="number"
              fullWidth
              size="small"
              value={form.previous_batch_hours}
              onChange={(event) => setForm({ ...form, previous_batch_hours: event.target.value })}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              label="History Days"
              fullWidth
              size="small"
              value={listToText(form.history_days)}
              onChange={(event) => setListField("history_days", event.target.value)}
            />
          </Grid>

          <Grid item xs={12} sx={{ my: 1 }}>
            <Divider sx={{ mb: 2 }} />
            <Typography variant="subtitle2" fontWeight={700} color="text.secondary">
              SAMPLING AND STATISTICS
            </Typography>
          </Grid>

          <Grid item xs={12} md={3}>
            <TextField
              label="Target Sample Per Group"
              type="number"
              fullWidth
              size="small"
              value={form.target_sample_per_group}
              onChange={(event) => setForm({ ...form, target_sample_per_group: event.target.value })}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <TextField
              label="Test Size"
              type="number"
              fullWidth
              size="small"
              value={form.test_size}
              onChange={(event) => setForm({ ...form, test_size: event.target.value })}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <TextField
              label="Random State"
              type="number"
              fullWidth
              size="small"
              value={form.random_state}
              onChange={(event) => setForm({ ...form, random_state: event.target.value })}
            />
          </Grid>
          <Grid item xs={12} sx={{ my: 1 }}>
            <Divider sx={{ mb: 2 }} />
            <Typography variant="subtitle2" fontWeight={700} color="text.secondary">
              FEATURE COLUMNS
            </Typography>
          </Grid>

          <Grid item xs={12} md={4}>
            <TextField
              label="Exclude Columns"
              fullWidth
              multiline
              minRows={3}
              size="small"
              value={listToText(form.exclude_cols)}
              onChange={(event) => setListField("exclude_cols", event.target.value)}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <TextField
              label="Categorical Columns"
              fullWidth
              multiline
              minRows={3}
              size="small"
              value={listToText(form.categorical_cols)}
              onChange={(event) => setListField("categorical_cols", event.target.value)}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <TextField
              label="Numeric Columns"
              fullWidth
              multiline
              minRows={3}
              size="small"
              value={listToText(form.numeric_cols)}
              onChange={(event) => setListField("numeric_cols", event.target.value)}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              label="Description"
              fullWidth
              multiline
              minRows={2}
              size="small"
              value={form.description}
              onChange={(event) => setForm({ ...form, description: event.target.value })}
            />
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions sx={{ p: 2, justifyContent: "space-between" }}>
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
          <Button variant="contained" startIcon={<SaveOutlined />} onClick={handleSave} disabled={saving}>
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
          <Typography variant="h6" fontWeight={700}>Anomaly Job Config Details</Typography>
        </Box>

        <Paper variant="outlined" sx={{ p: 3, borderRadius: 2 }}>
          <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 3, pb: 2, borderBottom: 1, borderColor: 'divider' }}>
            <Box>
              <Typography variant="caption" color="text.secondary" fontWeight={700}>SOURCE TABLE</Typography>
              <Typography variant="h6" fontWeight={800}>
                {tableNameById[selectedConfig.table_id] || selectedConfig.table_id?.substring(0, 8)}
              </Typography>
            </Box>
            <Stack direction="row" spacing={1}>
              {canUpdate && (
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
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle1" fontWeight={700} sx={{ mb: 2 }} color="primary">Execution Window</Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Paper variant="outlined" sx={{ p: 2, borderRadius: 1.5, bgcolor: 'action.hover' }}>
                    <Typography variant="caption" color="text.secondary" fontWeight={700}>BATCH TIME</Typography>
                    <Typography variant="body1" fontWeight={600} sx={{ mt: 0.5 }}>{selectedConfig.batch_time_col}</Typography>
                  </Paper>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Paper variant="outlined" sx={{ p: 2, borderRadius: 1.5, bgcolor: 'action.hover' }}>
                    <Typography variant="caption" color="text.secondary" fontWeight={700}>TEST SIZE</Typography>
                    <Typography variant="body1" fontWeight={600} sx={{ mt: 0.5 }}>{selectedConfig.test_size}</Typography>
                  </Paper>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Paper variant="outlined" sx={{ p: 2, borderRadius: 1.5, bgcolor: 'action.hover' }}>
                    <Typography variant="caption" color="text.secondary" fontWeight={700}>REQUIRED HISTORY DAYS</Typography>
                    <Typography variant="body1" fontWeight={600} sx={{ mt: 0.5 }}>{selectedConfig.required_history_days}</Typography>
                  </Paper>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Paper variant="outlined" sx={{ p: 2, borderRadius: 1.5, bgcolor: 'action.hover' }}>
                    <Typography variant="caption" color="text.secondary" fontWeight={700}>PREVIOUS BATCH HOURS</Typography>
                    <Typography variant="body1" fontWeight={600} sx={{ mt: 0.5 }}>{selectedConfig.previous_batch_hours}</Typography>
                  </Paper>
                </Grid>
                <Grid item xs={12}>
                  <Paper variant="outlined" sx={{ p: 2, borderRadius: 1.5, bgcolor: 'action.hover' }}>
                    <Typography variant="caption" color="text.secondary" fontWeight={700}>HISTORY DAYS</Typography>
                    <Stack direction="row" spacing={0.5} flexWrap="wrap" useFlexGap sx={{ mt: 1 }}>
                      {(selectedConfig.history_days || []).map((day) => <Chip key={day} label={day} size="small" />)}
                    </Stack>
                  </Paper>
                </Grid>
              </Grid>
            </Grid>

            <Grid item xs={12} md={6}>
              <Typography variant="subtitle1" fontWeight={700} sx={{ mb: 2 }} color="primary">Feature & Other Details</Typography>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Paper variant="outlined" sx={{ p: 2, borderRadius: 1.5, bgcolor: 'action.hover' }}>
                    <Typography variant="caption" color="text.secondary" fontWeight={700}>FEATURE COLUMNS</Typography>
                    <Typography variant="body2" sx={{ overflowWrap: "anywhere", mt: 1 }}>
                      <strong>Exclude:</strong> {listToText(selectedConfig.exclude_cols) || "-"}
                    </Typography>
                    <Typography variant="body2" sx={{ overflowWrap: "anywhere", mt: 1 }}>
                      <strong>Categorical:</strong> {listToText(selectedConfig.categorical_cols) || "-"}
                    </Typography>
                    <Typography variant="body2" sx={{ overflowWrap: "anywhere", mt: 1 }}>
                      <strong>Numeric:</strong> {listToText(selectedConfig.numeric_cols) || "-"}
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={12}>
                  <Paper variant="outlined" sx={{ p: 2, borderRadius: 1.5, bgcolor: 'action.hover' }}>
                    <Typography variant="caption" color="text.secondary" fontWeight={700}>DESCRIPTION</Typography>
                    <Typography variant="body1" sx={{ mt: 0.5 }}>{selectedConfig.description || "-"}</Typography>
                  </Paper>
                </Grid>
              </Grid>
            </Grid>
          </Grid>
        </Paper>

        {configDialog}
      </Box>
    );
  }

  return (
    <Box sx={{ p: 0, pt: 1 }}>
      <Box sx={{ display: "flex", justifyContent: "space-between", mb: 3, alignItems: "center" }}>
        <Box>
          <Typography variant="h5" fontWeight={800} color="primary">
            Anomaly job config
          </Typography>
          <Typography variant="body2" color="text.secondary">Configure settings and detection rules for anomaly detection tasks.</Typography>
        </Box>
        <Stack direction="row" spacing={1}>
          {canUpdate && (
            <Button startIcon={<AddOutlined />} variant="contained" onClick={handleOpenAdd}>
              New config
            </Button>
          )}
        </Stack>
      </Box>

      <StateBox loading={configs.loading} error={configs.error} empty={configItems.length === 0}>
        <TableContainer component={Paper} variant="outlined" sx={{ borderRadius: 2, overflow: 'hidden' }}>
          <Table size="small">
            <TableHead>
              <TableRow sx={{ bgcolor: "primary.main" }}>
                <TableCell sx={{ color: "white", fontWeight: "bold" }}>Source Table</TableCell>
                <TableCell sx={{ color: "white", fontWeight: "bold" }}>Batch Time</TableCell>
                <TableCell sx={{ color: "white", fontWeight: "bold" }}>History Days</TableCell>
                <TableCell align="right" sx={{ color: "white", fontWeight: "bold" }}>
                  Test Size
                </TableCell>
                <TableCell align="right" sx={{ color: "white", fontWeight: "bold" }}>
                  Actions
                </TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {configItems.map((row) => (
                <TableRow
                  key={row.id}
                  hover
                  onClick={() => setSelectedId(row.id)}
                  sx={{ cursor: "pointer" }}
                >
                  <TableCell sx={{ fontWeight: 600, whiteSpace: "nowrap" }}>
                    {tableNameById[row.table_id] || row.table_id?.substring(0, 8)}
                  </TableCell>
                  <TableCell>{row.batch_time_col}</TableCell>
                  <TableCell>
                    <Stack direction="row" spacing={0.5} flexWrap="wrap" useFlexGap>
                      {(row.history_days || []).map((day) => (
                        <Chip key={day} label={day} size="small" />
                      ))}
                    </Stack>
                  </TableCell>
                  <TableCell align="right">{row.test_size}</TableCell>
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
            onPageChange={(event, newPage) => setPage(newPage)}
            onRowsPerPageChange={(event) => {
              setPageSize(parseInt(event.target.value, 10));
              setPage(0);
            }}
          />
        </TableContainer>
      </StateBox>

      {configDialog}
    </Box>
  );
}

export default Config;
