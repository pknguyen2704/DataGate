import React from "react";
import {
  Alert,
  Button,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  MenuItem,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Tooltip,
  Typography,
} from "@mui/material";
import {
  AddOutlined as AddIcon,
  CheckCircleOutlineOutlined as ActivateIcon,
  DeleteOutline as DeleteIcon,
  EditOutlined as EditIcon,
  VisibilityOutlined as ViewIcon,
} from "@mui/icons-material";
import { rulesApi } from "~/apis/api";
import { datagateColors, panelSx } from "~/theme";

const constraintTypes = ["not_null", "non_negative", "unique", "value_range", "range_check", "regex"];

const emptyForm = {
  column_name: "",
  constraint_type: "not_null",
  description: "",
};

function RuleManagement({ tableId, columns = [] }) {
  const [rules, setRules] = React.useState([]);
  const [error, setError] = React.useState(null);
  const [dialogMode, setDialogMode] = React.useState(null);
  const [selectedRule, setSelectedRule] = React.useState(null);
  const [form, setForm] = React.useState(emptyForm);
  const [topK, setTopK] = React.useState(20);

  const loadRules = React.useCallback(() => {
    if (!tableId) return;
    rulesApi.list({ table_id: tableId, top_k: topK })
      .then((response) => setRules(response.data || []))
      .catch((err) => setError(err?.response?.data?.detail || "Could not load rules."));
  }, [tableId, topK]);

  React.useEffect(() => {
    loadRules();
  }, [loadRules]);

  const openCreate = () => {
    setSelectedRule(null);
    setForm({ ...emptyForm, column_name: columns[0]?.name || columns[0]?.column_name || "" });
    setDialogMode("create");
  };

  const openDialog = (mode, rule) => {
    setSelectedRule(rule);
    setForm({ ...emptyForm, ...rule });
    setDialogMode(mode);
  };

  const closeDialog = () => {
    setDialogMode(null);
    setSelectedRule(null);
    setForm(emptyForm);
  };

  const handleSubmit = () => {
    const payload = {
      column_name: form.column_name,
      constraint_type: form.constraint_type,
      description: form.description || null,
    };

    const request = dialogMode === "create"
      ? rulesApi.create({ ...payload, table_id: tableId })
      : rulesApi.update(selectedRule.id, payload);

    request
      .then(() => {
        closeDialog();
        loadRules();
      })
      .catch((err) => setError(err?.response?.data?.detail || "Could not save rule."));
  };

  const handleDelete = (ruleId) => {
    rulesApi.delete(ruleId)
      .then(loadRules)
      .catch((err) => setError(err?.response?.data?.detail || "Could not delete rule."));
  };

  const handleActivate = (ruleId) => {
    rulesApi.updateStatus(ruleId, "active")
      .then(loadRules)
      .catch((err) => setError(err?.response?.data?.detail || "Could not activate rule."));
  };

  const statusCounts = React.useMemo(() => ({
    active: rules.filter((rule) => rule.status === "active").length,
    pending: rules.filter((rule) => rule.status === "pending").length,
    system: rules.filter((rule) => rule.created_by === "system").length,
  }), [rules]);

  const readOnly = dialogMode === "view";

  return (
    <Stack spacing={3}>
      <Paper sx={{ ...panelSx, p: 3 }}>
        <Stack direction={{ xs: "column", xl: "row" }} spacing={2} justifyContent="space-between">
          <Stack spacing={1.5}>
            <Typography variant="h6" fontWeight={800}>Rules for this table only</Typography>
            <Typography color="text.secondary">
              Auto-generated rules stay attached to this table, accumulate frequency over multiple batches, and can be activated once approved.
            </Typography>
            <Stack direction="row" spacing={1} flexWrap="wrap">
              <Chip size="small" color="success" label={`${statusCounts.active} active`} />
              <Chip size="small" color="warning" label={`${statusCounts.pending} pending`} />
              <Chip size="small" variant="outlined" label={`${statusCounts.system} system rules`} />
            </Stack>
          </Stack>

          <Stack direction={{ xs: "column", sm: "row" }} spacing={1.5}>
            <TextField
              select
              size="small"
              label="Top K"
              value={topK}
              onChange={(event) => setTopK(Number(event.target.value))}
              sx={{ minWidth: 110 }}
            >
              {[10, 20, 50, 100].map((value) => (
                <MenuItem key={value} value={value}>{value}</MenuItem>
              ))}
            </TextField>
            <Button variant="contained" startIcon={<AddIcon />} onClick={openCreate} disabled={!tableId}>
              Add rule
            </Button>
          </Stack>
        </Stack>
      </Paper>

      {error ? <Alert severity="warning" onClose={() => setError(null)}>{error}</Alert> : null}

      <Paper sx={{ ...panelSx, overflow: "hidden" }}>
        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Column</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Created by</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Frequency</TableCell>
                <TableCell>Last batch</TableCell>
                <TableCell>Description</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rules.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={8} align="center" sx={{ py: 7, color: "text.secondary" }}>
                    No rules available for this table.
                  </TableCell>
                </TableRow>
              ) : (
                rules.map((rule) => (
                  <TableRow key={rule.id} hover>
                    <TableCell sx={{ fontWeight: 700 }}>{rule.column_name}</TableCell>
                    <TableCell>{rule.constraint_type}</TableCell>
                    <TableCell>
                      <Chip
                        size="small"
                        label={rule.created_by}
                        variant={rule.created_by === "system" ? "filled" : "outlined"}
                        color={rule.created_by === "system" ? "primary" : "default"}
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        size="small"
                        label={rule.status}
                        color={rule.status === "active" ? "success" : rule.status === "pending" ? "warning" : "default"}
                      />
                    </TableCell>
                    <TableCell>{rule.frequency ?? 1}</TableCell>
                    <TableCell>{rule.last_seen_at_date_hour || rule.updated_at?.slice?.(0, 19) || "--"}</TableCell>
                    <TableCell sx={{ maxWidth: 420, color: datagateColors.textSecondary }}>
                      {rule.description || "--"}
                    </TableCell>
                    <TableCell align="right">
                      {rule.status === "pending" ? (
                        <Tooltip title="Activate rule">
                          <IconButton size="small" color="success" onClick={() => handleActivate(rule.id)}>
                            <ActivateIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      ) : null}
                      <Tooltip title="View detail">
                        <IconButton size="small" onClick={() => openDialog("view", rule)}>
                          <ViewIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Update">
                        <IconButton size="small" onClick={() => openDialog("edit", rule)}>
                          <EditIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete">
                        <IconButton size="small" color="error" onClick={() => handleDelete(rule.id)}>
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      <Dialog open={Boolean(dialogMode)} onClose={closeDialog} fullWidth maxWidth="sm">
        <DialogTitle>
          {dialogMode === "create" ? "Add manual rule" : dialogMode === "edit" ? "Update rule" : "Rule detail"}
        </DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField
              select
              label="Column"
              value={form.column_name}
              disabled={readOnly || dialogMode === "edit"}
              onChange={(event) => setForm((prev) => ({ ...prev, column_name: event.target.value }))}
            >
              {columns.map((column) => {
                const name = column.name || column.column_name;
                return <MenuItem key={name} value={name}>{name}</MenuItem>;
              })}
            </TextField>
            <TextField
              select
              label="Constraint type"
              value={form.constraint_type}
              disabled={readOnly || dialogMode === "edit"}
              onChange={(event) => setForm((prev) => ({ ...prev, constraint_type: event.target.value }))}
            >
              {constraintTypes.map((type) => <MenuItem key={type} value={type}>{type}</MenuItem>)}
            </TextField>
            <TextField
              label="Description"
              value={form.description || ""}
              disabled={readOnly}
              multiline
              minRows={3}
              onChange={(event) => setForm((prev) => ({ ...prev, description: event.target.value }))}
            />
            {selectedRule ? (
              <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
                <TextField label="Created by" value={form.created_by || "manual"} disabled fullWidth />
                <TextField label="Frequency" value={form.frequency ?? 1} disabled fullWidth />
              </Stack>
            ) : null}
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={closeDialog}>Close</Button>
          {!readOnly ? <Button variant="contained" onClick={handleSubmit}>Save</Button> : null}
        </DialogActions>
      </Dialog>
    </Stack>
  );
}

export default RuleManagement;
