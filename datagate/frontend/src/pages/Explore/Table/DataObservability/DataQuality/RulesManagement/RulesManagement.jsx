import React, { useEffect, useMemo, useState } from "react";
import {
  Box,
  Button,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Grid,
  IconButton,
  MenuItem,
  Paper,
  Stack,
  Switch,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";
import {
  Add as AddIcon,
  AutoFixHigh as SuggestIcon,
  Edit as EditIcon,
  PlayArrow as RunIcon,
  Tune as TuneIcon,
} from "@mui/icons-material";
import { toast } from "react-toastify";
import { Area, AreaChart, ResponsiveContainer } from "recharts";
import { rulesApi } from "~/apis/rules";
import { datagateColors, panelSx, subtlePanelSx } from "~/theme";

const DEFAULT_FORM = (tableName) => ({
  table_name: tableName || "",
  column_name: "",
  rule_type: "completeness",
  rule_expression: "",
  is_active: true,
  is_applied: false,
  priority: "medium",
  category: "validity",
  source: "manual",
  description: "",
});

const failureTrend = [
  { d: "M", v: 2 },
  { d: "T", v: 4 },
  { d: "W", v: 3 },
  { d: "T", v: 8 },
  { d: "F", v: 5 },
  { d: "S", v: 2 },
  { d: "S", v: 3 },
];

const failedPreview = [101, 105, 122];

function RulesManagement({ assetDetail, tableName: tableNameProp }) {
  const tableName = tableNameProp || assetDetail?.table_name;
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const [editingRule, setEditingRule] = useState(null);
  const [activeRuleId, setActiveRuleId] = useState(null);
  const [formData, setFormData] = useState(DEFAULT_FORM(tableName));

  const fetchRules = async (targetTableName) => {
    if (!targetTableName) {
      setRules([]);
      return;
    }

    setLoading(true);
    try {
      const response = await rulesApi.getRules(targetTableName);
      setRules(response.data || []);
    } catch {
      toast.error("Failed to fetch rules");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setFormData(DEFAULT_FORM(tableName));
    setEditingRule(null);
    setActiveRuleId(null);
    fetchRules(tableName);
  }, [tableName]);

  const selectedRule = useMemo(
    () => rules.find((rule) => rule.id === activeRuleId) || null,
    [activeRuleId, rules]
  );

  const openCreateDialog = () => {
    setEditingRule(null);
    setFormData(DEFAULT_FORM(tableName));
    setOpen(true);
  };

  const openEditDialog = (rule) => {
    setEditingRule(rule);
    setFormData({
      table_name: rule.table_name || tableName,
      column_name: rule.column_name || "",
      rule_type: rule.rule_type || "completeness",
      rule_expression: rule.rule_expression || "",
      is_active: rule.is_active ?? true,
      is_applied: rule.is_applied ?? false,
      priority: rule.priority || "medium",
      category: rule.category || "validity",
      source: rule.source || "manual",
      description: rule.description || "",
    });
    setOpen(true);
  };

  const handleToggleActive = async (ruleId, currentStatus) => {
    try {
      await rulesApi.updateRule(ruleId, { is_active: !currentStatus });
      setRules((prev) =>
        prev.map((rule) =>
          rule.id === ruleId ? { ...rule, is_active: !currentStatus } : rule
        )
      );
      toast.success("Rule status updated");
    } catch {
      toast.error("Failed to update status");
    }
  };

  const handleSaveRule = async () => {
    try {
      if (editingRule) {
        await rulesApi.updateRule(editingRule.id, formData);
        toast.success("Rule updated");
      } else {
        await rulesApi.createRule(formData);
        toast.success("Rule created");
      }

      setOpen(false);
      fetchRules(tableName);
    } catch {
      toast.error("Operation failed");
    }
  };

  const handleToggleApplied = async (ruleId, currentStatus) => {
    try {
      await rulesApi.updateRule(ruleId, { is_applied: !currentStatus });
      setRules((prev) =>
        prev.map((rule) =>
          rule.id === ruleId ? { ...rule, is_applied: !currentStatus } : rule
        )
      );
      toast.success("Rule apply status updated");
    } catch {
      toast.error("Failed to update apply status");
    }
  };

  const handleGenerateSuggestions = async () => {
    try {
      await rulesApi.triggerSuggestions({ table_name: tableName });
      toast.success("Rule suggestion job triggered");
      fetchRules(tableName);
    } catch {
      toast.error("Failed to trigger rule suggestion job");
    }
  };

  const handleValidateAppliedRules = async () => {
    try {
      await rulesApi.triggerValidation({ table_name: tableName });
      toast.success("Rule validation job triggered");
    } catch {
      toast.error("Failed to trigger rule validation job");
    }
  };

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={selectedRule ? 7 : 12}>
        <Paper sx={{ ...panelSx, overflow: "hidden" }}>
          <Box
            sx={{
              p: 2.5,
              borderBottom: "1px solid",
              borderColor: "divider",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              gap: 2,
            }}
          >
            <Box>
              <Typography variant="h6" fontWeight={700}>
                Rules for {assetDetail?.asset_name || tableName}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Manage quality constraints at table scope.
              </Typography>
            </Box>
            <Stack direction="row" spacing={1}>
              <Button variant="outlined" startIcon={<SuggestIcon />} onClick={handleGenerateSuggestions}>
                Suggest Rules
              </Button>
              <Button variant="outlined" startIcon={<RunIcon />} onClick={handleValidateAppliedRules}>
                Validate Applied
              </Button>
              <Button variant="contained" startIcon={<AddIcon />} onClick={openCreateDialog}>
                Add Quality Rule
              </Button>
            </Stack>
          </Box>

          <TableContainer>
            <Table size="small">
              <TableHead sx={{ bgcolor: datagateColors.tableHeadBackground }}>
                <TableRow>
                  <TableCell sx={{ fontWeight: 700 }}>Column</TableCell>
                  <TableCell sx={{ fontWeight: 700 }}>Rule</TableCell>
                  <TableCell sx={{ fontWeight: 700 }}>Category</TableCell>
                  <TableCell sx={{ fontWeight: 700 }}>Priority</TableCell>
                  <TableCell sx={{ fontWeight: 700 }}>Applied</TableCell>
                  <TableCell sx={{ fontWeight: 700 }}>Enabled</TableCell>
                  <TableCell sx={{ fontWeight: 700 }}>Last Result</TableCell>
                  <TableCell sx={{ fontWeight: 700 }} align="right">
                    Action
                  </TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {loading ? (
                  <TableRow>
                    <TableCell colSpan={8} align="center" sx={{ py: 4 }}>
                      <CircularProgress size={24} />
                    </TableCell>
                  </TableRow>
                ) : rules.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={8} align="center" sx={{ py: 6 }}>
                      <Typography color="text.secondary">
                        No rules configured for this table yet.
                      </Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  rules.map((rule) => (
                    <TableRow
                      key={rule.id}
                      hover
                      selected={activeRuleId === rule.id}
                      onClick={() => setActiveRuleId(rule.id)}
                      sx={{ cursor: "pointer" }}
                    >
                      <TableCell sx={{ fontWeight: 600 }}>{rule.column_name}</TableCell>
                      <TableCell>
                        <Chip
                          label={rule.rule_type}
                          size="small"
                          variant="outlined"
                          sx={{ fontWeight: 600 }}
                        />
                      </TableCell>
                      <TableCell>
                        <Chip label={rule.category || "validity"} size="small" />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={rule.priority || "medium"}
                          size="small"
                          color={
                            rule.priority === "high"
                              ? "error"
                              : rule.priority === "medium"
                                ? "warning"
                                : "default"
                          }
                        />
                      </TableCell>
                      <TableCell>
                        <Switch
                          size="small"
                          checked={Boolean(rule.is_applied)}
                          onChange={(event) => {
                            event.stopPropagation();
                            handleToggleApplied(rule.id, rule.is_applied);
                          }}
                        />
                      </TableCell>
                      <TableCell>
                        <Switch
                          size="small"
                          checked={Boolean(rule.is_active)}
                          onChange={(event) => {
                            event.stopPropagation();
                            handleToggleActive(rule.id, rule.is_active);
                          }}
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" sx={{ fontWeight: 700 }}>
                          {rule.last_result_status || "--"}
                        </Typography>
                        {rule.last_failure_message ? (
                          <Typography variant="caption" color="error.main">
                            {rule.last_failure_message}
                          </Typography>
                        ) : null}
                      </TableCell>
                      <TableCell align="right">
                        <IconButton
                          size="small"
                          onClick={(event) => {
                            event.stopPropagation();
                            openEditDialog(rule);
                          }}
                        >
                          <EditIcon fontSize="small" />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      </Grid>

      {selectedRule ? (
        <Grid item xs={12} md={5}>
          <Paper sx={{ ...panelSx, p: 3, height: "100%", position: "sticky", top: 24 }}>
            <Box sx={{ display: "flex", justifyContent: "space-between", mb: 2 }}>
              <Typography variant="h6" fontWeight={700}>
                Rule Details
              </Typography>
              <IconButton size="small" onClick={() => setActiveRuleId(null)}>
                <TuneIcon fontSize="small" />
              </IconButton>
            </Box>

            <Box sx={{ ...subtlePanelSx, p: 2, mb: 3 }}>
              <Typography variant="caption" color="text.secondary" fontWeight={700}>
                SQL DEFINITION
              </Typography>
              <Typography
                variant="body2"
                sx={{ fontFamily: "Fira Code, monospace", mt: 1, color: "primary.dark" }}
              >
                {selectedRule.rule_expression ||
                  `SELECT * FROM ${tableName} WHERE ${selectedRule.column_name} IS NULL`}
              </Typography>
              <Typography variant="body2" sx={{ mt: 1 }}>
                Source: {selectedRule.source || "manual"} | Category: {selectedRule.category || "validity"} |
                Priority: {selectedRule.priority || "medium"} | Applied: {selectedRule.is_applied ? "Yes" : "No"}
              </Typography>
            </Box>

            <Typography variant="subtitle2" fontWeight={700} gutterBottom>
              Failure Trend
            </Typography>
            <Box sx={{ height: 160, mb: 3 }}>
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={failureTrend}>
                  <Area
                    type="monotone"
                    dataKey="v"
                    stroke="#EF4444"
                    fill="#EF4444"
                    fillOpacity={0.1}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </Box>

            <Typography variant="subtitle2" fontWeight={700} gutterBottom>
              Failed Records Preview
            </Typography>
            <TableContainer sx={{ border: `1px solid ${datagateColors.cardBorder}`, borderRadius: "8px" }}>
              <Table size="small">
                <TableHead sx={{ bgcolor: datagateColors.tableHeadBackground }}>
                  <TableRow>
                    <TableCell sx={{ fontSize: "10px", fontWeight: 700 }}>ID</TableCell>
                    <TableCell sx={{ fontSize: "10px", fontWeight: 700 }}>Value</TableCell>
                    <TableCell sx={{ fontSize: "10px", fontWeight: 700 }}>At</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {failedPreview.map((id) => (
                    <TableRow key={id}>
                      <TableCell sx={{ fontSize: "11px" }}>#{id}</TableCell>
                      <TableCell sx={{ fontSize: "11px", color: "error.main" }}>NULL</TableCell>
                      <TableCell sx={{ fontSize: "11px" }}>2h ago</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>

            <Button fullWidth variant="outlined" sx={{ mt: 3 }} startIcon={<RunIcon />} onClick={handleValidateAppliedRules}>
              Run Validation Now
            </Button>
          </Paper>
        </Grid>
      ) : null}

      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ fontWeight: 800 }}>
          {editingRule ? "Edit Quality Rule" : "New Quality Rule"}
        </DialogTitle>
        <DialogContent dividers>
          <Stack spacing={3} sx={{ mt: 1 }}>
            <TextField
              label="Target Column"
              fullWidth
              value={formData.column_name}
              onChange={(event) =>
                setFormData((prev) => ({ ...prev, column_name: event.target.value }))
              }
            />
            <TextField
              select
              label="Rule Type"
              fullWidth
              value={formData.rule_type}
              onChange={(event) =>
                setFormData((prev) => ({ ...prev, rule_type: event.target.value }))
              }
            >
              <MenuItem value="completeness">Completeness (Not Null)</MenuItem>
              <MenuItem value="uniqueness">Uniqueness</MenuItem>
              <MenuItem value="compliance">Custom SQL Compliance</MenuItem>
              <MenuItem value="range">Range Check</MenuItem>
            </TextField>
            <TextField
              label="SQL Expression / Threshold"
              multiline
              rows={3}
              fullWidth
              value={formData.rule_expression}
              onChange={(event) =>
                setFormData((prev) => ({ ...prev, rule_expression: event.target.value }))
              }
            />
            <TextField
              select
              label="Category"
              fullWidth
              value={formData.category}
              onChange={(event) =>
                setFormData((prev) => ({ ...prev, category: event.target.value }))
              }
            >
              <MenuItem value="completeness">Completeness</MenuItem>
              <MenuItem value="uniqueness">Uniqueness</MenuItem>
              <MenuItem value="compliance">Compliance</MenuItem>
              <MenuItem value="range">Range</MenuItem>
              <MenuItem value="distribution">Distribution</MenuItem>
              <MenuItem value="validity">Validity</MenuItem>
            </TextField>
            <TextField
              select
              label="Priority"
              fullWidth
              value={formData.priority}
              onChange={(event) =>
                setFormData((prev) => ({ ...prev, priority: event.target.value }))
              }
            >
              <MenuItem value="high">High</MenuItem>
              <MenuItem value="medium">Medium</MenuItem>
              <MenuItem value="low">Low</MenuItem>
            </TextField>
            <TextField
              label="Description"
              multiline
              rows={2}
              fullWidth
              value={formData.description || ""}
              onChange={(event) =>
                setFormData((prev) => ({ ...prev, description: event.target.value }))
              }
            />
          </Stack>
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleSaveRule}>
            Save Rule
          </Button>
        </DialogActions>
      </Dialog>
    </Grid>
  );
}

export default RulesManagement;
