import React, { useState, useEffect } from 'react';
import { 
  Box, Typography, Paper, Table, TableBody, 
  TableCell, TableContainer, TableHead, TableRow, 
  Switch, IconButton, Button, Dialog, DialogTitle, 
  DialogContent, DialogActions, TextField, MenuItem,
  Chip, CircularProgress, Breadcrumbs, Link,
  Stack, Card, CardContent, Divider,
} from '@mui/material';
import { 
  Add as AddIcon, 
  Edit as EditIcon, 
  Delete as DeleteIcon,
  RuleOutlined as RuleIcon,
  Search as SearchIcon,
  PlayArrow as RunIcon,
  Tune as TuneIcon,
} from '@mui/icons-material';
import { useLocation, useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import { rulesApi } from '../../apis/rules';
import { AreaChart, Area, ResponsiveContainer, Tooltip as ChartTooltip } from 'recharts';

const Rules = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const tableParam = searchParams.get('table');

  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const [editingRule, setEditingRule] = useState(null);
  const [activeRuleId, setActiveRuleId] = useState(null);

  const [formData, setFormData] = useState({
    table_name: tableParam || '',
    column_name: '',
    rule_type: 'completeness',
    rule_expression: '',
    is_active: true
  });

  const fetchRules = async (tableName) => {
    setLoading(true);
    try {
      const res = await rulesApi.getRules(tableName);
      setRules(res.data);
    } catch (err) { toast.error("Failed to fetch rules"); }
    finally { setLoading(false); }
  };

  useEffect(() => {
    if (tableParam) fetchRules(tableParam);
  }, [tableParam]);

  const handleToggleActive = async (ruleId, currentStatus) => {
    try {
      await rulesApi.updateRule(ruleId, { is_active: !currentStatus });
      setRules(rules.map(r => r.id === ruleId ? { ...r, is_active: !currentStatus } : r));
      toast.success("Rule status updated");
    } catch (err) { toast.error("Failed to update status"); }
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
      fetchRules(tableParam);
    } catch (err) { toast.error("Operation failed"); }
  };

  const selectedRule = rules.find(r => r.id === activeRuleId);

  if (!tableParam) {
    return (
      <Box p={4} textAlign="center">
        <Typography variant="h4" gutterBottom>Rule Validation</Typography>
        <Typography variant="body1" color="text.secondary">Select an asset to manage its logic and quality constraints.</Typography>
        <Button variant="contained" sx={{ mt: 3 }} onClick={() => navigate('/observability')}>Go to Assets</Button>
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
        <Box>
          <Breadcrumbs sx={{ mb: 0.5 }}>
            <Link underline="hover" color="inherit" onClick={() => navigate('/observability')} sx={{ cursor: 'pointer' }}>Observability</Link>
            <Typography color="text.primary">{tableParam}</Typography>
          </Breadcrumbs>
          <Typography variant="h4" sx={{ fontWeight: 800 }}>Rule Validation</Typography>
        </Box>
        <Button variant="contained" startIcon={<AddIcon />} onClick={() => { setEditingRule(null); setOpen(true); }}>
          Add Quality Rule
        </Button>
      </Box>

      <Grid container spacing={3}>
        {/* Left Table Panel */}
        <Grid item xs={12} md={selectedRule ? 7 : 12}>
          <Paper>
            <Box sx={{ p: 2.5, borderBottom: '1px solid', borderColor: 'divider' }}>
              <Typography variant="h6">Rules for {tableParam}</Typography>
            </Box>
            <TableContainer>
              <Table size="small">
                <TableHead sx={{ bgcolor: '#F8FAFC' }}>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 700 }}>Column</TableCell>
                    <TableCell sx={{ fontWeight: 700 }}>Rule</TableCell>
                    <TableCell sx={{ fontWeight: 700 }}>Status</TableCell>
                    <TableCell sx={{ fontWeight: 700 }}>Failure Rate</TableCell>
                    <TableCell sx={{ fontWeight: 700 }} align="right">Action</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {loading ? (
                    <TableRow><TableCell colSpan={5} align="center" sx={{ py: 4 }}><CircularProgress size={24} /></TableCell></TableRow>
                  ) : rules.map((rule) => (
                    <TableRow 
                      key={rule.id} 
                      hover 
                      selected={activeRuleId === rule.id}
                      onClick={() => setActiveRuleId(rule.id)}
                      sx={{ cursor: 'pointer' }}
                    >
                      <TableCell sx={{ fontWeight: 600 }}>{rule.column_name}</TableCell>
                      <TableCell><Chip label={rule.rule_type} size="small" variant="outlined" sx={{ fontWeight: 600 }} /></TableCell>
                      <TableCell>
                         <Switch 
                           size="small"
                           checked={rule.is_active} 
                           onChange={(e) => { e.stopPropagation(); handleToggleActive(rule.id, rule.is_active); }}
                         />
                      </TableCell>
                      <TableCell>
                         <Typography variant="body2" color={rule.failure_rate > 5 ? 'error.main' : 'success.main'} sx={{ fontWeight: 700 }}>
                            {rule.failure_rate || 0}%
                         </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <IconButton size="small" onClick={(e) => { e.stopPropagation(); setEditingRule(rule); setOpen(true); }}>
                          <EditIcon fontSize="small" />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>

        {/* Right Detail Panel */}
        {selectedRule && (
          <Grid item xs={12} md={5}>
            <Paper sx={{ p: 3, height: '100%', position: 'sticky', top: 24 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="h6">Rule Details</Typography>
                <IconButton size="small" onClick={() => setActiveRuleId(null)}><TuneIcon fontSize="small" /></IconButton>
              </Box>
              
              <Box sx={{ p: 2, bgcolor: '#F8FAFC', borderRadius: '12px', mb: 3 }}>
                <Typography variant="caption" color="text.secondary" fontWeight={700}>SQL DEFINITION</Typography>
                <Typography variant="body2" sx={{ fontFamily: 'Fira Code', mt: 1, color: 'primary.dark' }}>
                  {selectedRule.rule_expression || `SELECT * FROM ${tableParam} WHERE ${selectedRule.column_name} IS NULL`}
                </Typography>
              </Box>

              <Typography variant="subtitle2" fontWeight={700} gutterBottom>Failure Trend</Typography>
              <Box sx={{ height: 160, mb: 3 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={[
                    { d: 'M', v: 2 }, { d: 'T', v: 4 }, { d: 'W', v: 3 }, { d: 'T', v: 8 }, { d: 'F', v: 5 }, { d: 'S', v: 2 }, { d: 'S', v: 3 }
                  ]}>
                    <Area type="monotone" dataKey="v" stroke="#EF4444" fill="#EF4444" fillOpacity={0.1} />
                  </AreaChart>
                </ResponsiveContainer>
              </Box>

              <Typography variant="subtitle2" fontWeight={700} gutterBottom>Failed Records Preview</Typography>
              <TableContainer sx={{ border: '1px solid #E2E8F0', borderRadius: '8px' }}>
                <Table size="small">
                  <TableHead sx={{ bgcolor: '#F8FAFC' }}>
                    <TableRow>
                      <TableCell sx={{ fontSize: '10px', fontWeight: 700 }}>ID</TableCell>
                      <TableCell sx={{ fontSize: '10px', fontWeight: 700 }}>Value</TableCell>
                      <TableCell sx={{ fontSize: '10px', fontWeight: 700 }}>At</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {[101, 105, 122].map(id => (
                      <TableRow key={id}>
                        <TableCell sx={{ fontSize: '11px' }}>#{id}</TableCell>
                        <TableCell sx={{ fontSize: '11px', color: 'error.main' }}>NULL</TableCell>
                        <TableCell sx={{ fontSize: '11px' }}>2h ago</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
              
              <Button fullWidth variant="outlined" sx={{ mt: 3 }} startIcon={<RunIcon />}>Run Validation Now</Button>
            </Paper>
          </Grid>
        )}
      </Grid>

      {/* Save Dialog */}
      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ fontWeight: 800 }}>{editingRule ? 'Edit Quality Rule' : 'New Quality Rule'}</DialogTitle>
        <DialogContent dividers>
          <Stack spacing={3} sx={{ mt: 1 }}>
            <TextField label="Target Column" fullWidth value={formData.column_name} onChange={e => setFormData({...formData, column_name: e.target.value})} />
            <TextField select label="Rule Type" fullWidth value={formData.rule_type} onChange={e => setFormData({...formData, rule_type: e.target.value})}>
              <MenuItem value="completeness">Completeness (Not Null)</MenuItem>
              <MenuItem value="uniqueness">Uniqueness</MenuItem>
              <MenuItem value="sql">Custom SQL Compliance</MenuItem>
              <MenuItem value="range">Range Check</MenuItem>
            </TextField>
            <TextField label="SQL Expression / Threshold" multiline rows={3} fullWidth value={formData.rule_expression} onChange={e => setFormData({...formData, rule_expression: e.target.value})} />
          </Stack>
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleSaveRule}>Save Rule</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Rules;