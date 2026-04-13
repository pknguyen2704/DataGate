import React, { useState, useEffect } from 'react';
import { 
  Box, Typography, Paper, Table, TableBody, 
  TableCell, TableContainer, TableHead, TableRow, 
  Switch, IconButton, Button, Dialog, DialogTitle, 
  DialogContent, DialogActions, TextField, MenuItem,
  Chip, CircularProgress, Breadcrumbs, Link,
  Tooltip, Alert, FormControlLabel, FormGroup, Checkbox
} from '@mui/material';
import { 
  Add as AddIcon, 
  Edit as EditIcon, 
  Delete as DeleteIcon,
  FilterList as SortIcon,
  PlayCircleOutline as RunIcon,
  Dataset as DatasetIcon
} from '@mui/icons-material';
import { useLocation } from 'react-router-dom';
import { toast } from 'react-toastify';
import { rulesApi } from '../../apis/rules';

const Rules = () => {
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const [editingRule, setEditingRule] = useState(null);
  
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const tableParam = searchParams.get('table');

  const [formData, setFormData] = useState({
    table_name: tableParam || '',
    column_name: '',
    rule_type: 'not_null',
    rule_expression: '',
    is_active: true
  });

  useEffect(() => {
    if (tableParam) {
      setFormData(prev => ({ ...prev, table_name: tableParam || '' }));
      fetchRules(tableParam);
    }
  }, [tableParam]);

  const fetchRules = async (tableName) => {
    setLoading(true);
    try {
      const res = await rulesApi.getRules(tableName);
      setRules(res.data);
    } catch (err) {
      toast.error("Failed to fetch rules");
    } finally {
      setLoading(false);
    }
  };

  const handleToggleActive = async (ruleId, currentStatus) => {
    try {
      await rulesApi.updateRule(ruleId, { is_active: !currentStatus });
      setRules(rules.map(r => r.id === ruleId ? { ...r, is_active: !currentStatus } : r));
      toast.success("Rule status updated");
    } catch (err) {
      toast.error("Failed to update status");
    }
  };

  const handleDeleteRule = async (id) => {
    if (window.confirm("Delete this rule?")) {
      try {
        await rulesApi.deleteRule(id);
        setRules(rules.filter(r => r.id !== id));
        toast.success("Rule deleted");
      } catch (err) {
        toast.error("Failed to delete");
      }
    }
  };

  const handleSaveRule = async () => {
    try {
      if (editingRule) {
        await rulesApi.updateRule(editingRule.id, formData);
        toast.success("Rule updated");
      } else {
        await rulesApi.createRule(formData);
        toast.success("Custom rule added");
      }
      setOpen(false);
      fetchRules(tableParam);
      setEditingRule(null);
      setFormData({ table_name: tableParam || '', column_name: '', rule_type: 'not_null', rule_expression: '', is_active: true });
    } catch (err) {
      toast.error("Save failed. Check if expression is unique.");
    }
  };

  const handleEdit = (rule) => {
    setEditingRule(rule);
    setFormData({
      table_name: rule.table_name,
      column_name: rule.column_name,
      rule_type: rule.rule_type,
      rule_expression: rule.rule_expression || '',
      is_active: rule.is_active
    });
    setOpen(true);
  };

  const getRuleTypeChip = (type) => {
    const colors = {
      not_null: 'primary',
      min_value: 'secondary',
      max_value: 'secondary',
      regex: 'info',
      custom: 'warning'
    };
    return <Chip label={type} size="small" variant="outlined" color={colors[type] || 'default'} sx={{ fontWeight: 700, borderRadius: 1.5 }} />;
  };

  if (!tableParam) {
    return (
      <Box p={4} textAlign="center">
        <Typography variant="h6" color="text.secondary">Select a table from the sidebar to manage its logic rules.</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 4, bgcolor: '#F8FAFC', minHeight: '100%' }}>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Breadcrumbs separator="/" sx={{ mb: 1 }}>
          <Link underline="hover" color="inherit" href="#">Service</Link>
          <Link underline="hover" color="inherit" href="#">{tableParam.split('.')[0] || 'catalog'}</Link>
          <Typography color="text.primary" fontWeight="600">{tableParam}</Typography>
        </Breadcrumbs>
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Box sx={{ bgcolor: 'primary.main', p: 1, borderRadius: 2, display: 'flex', color: 'white' }}>
              <RunIcon />
            </Box>
            <Box>
              <Typography variant="h4" fontWeight="800" sx={{ color: '#0F172A' }}>Rule Management</Typography>
              <Typography variant="body2" color="text.secondary">Define and activate quality rules for <strong>{tableParam}</strong></Typography>
            </Box>
          </Box>
          <Button 
            variant="contained" 
            startIcon={<AddIcon />} 
            onClick={() => setOpen(true)}
            sx={{ borderRadius: 2, textTransform: 'none', px: 3, boxShadow: 'none' }}
          >
            Add Custom Rule
          </Button>
        </Box>
      </Box>

      {/* Rules Table */}
      <TableContainer component={Paper} sx={{ borderRadius: 3, boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)', overflow: 'hidden' }}>
        <Table>
          <TableHead sx={{ bgcolor: '#F1F5F9' }}>
            <TableRow>
              <TableCell sx={{ fontWeight: 800 }}>Field</TableCell>
              <TableCell sx={{ fontWeight: 800 }}>Rule Type</TableCell>
              <TableCell sx={{ fontWeight: 800 }}>Rule Expression</TableCell>
              <TableCell sx={{ fontWeight: 800 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  Frequency <SortIcon fontSize="small" color="disabled" />
                </Box>
              </TableCell>
              <TableCell sx={{ fontWeight: 800 }}>Active</TableCell>
              <TableCell align="right" sx={{ fontWeight: 800 }}>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow><TableCell colSpan={6} align="center" sx={{ py: 10 }}><CircularProgress /></TableCell></TableRow>
            ) : rules.length === 0 ? (
              <TableRow><TableCell colSpan={6} align="center" sx={{ py: 5 }}><Typography color="text.secondary">No rules found for this table.</Typography></TableCell></TableRow>
            ) : rules.map((rule) => (
              <TableRow key={rule.id} hover>
                <TableCell sx={{ fontWeight: 600 }}>{rule.column_name}</TableCell>
                <TableCell>{getRuleTypeChip(rule.rule_type)}</TableCell>
                <TableCell sx={{ fontFamily: 'monospace', color: 'text.secondary', maxWidth: 300, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {rule.rule_expression}
                </TableCell>
                <TableCell>
                   <Chip label={rule.frequency} size="small" sx={{ bgcolor: '#F0F9FF', color: '#0369A1', fontWeight: 600 }} />
                </TableCell>
                <TableCell>
                  <Switch 
                    checked={rule.is_active} 
                    onChange={() => handleToggleActive(rule.id, rule.is_active)}
                    color="primary"
                  />
                </TableCell>
                <TableCell align="right">
                  <Tooltip title="Edit">
                    <IconButton size="small" onClick={() => handleEdit(rule)}><EditIcon fontSize="small" /></IconButton>
                  </Tooltip>
                  <Tooltip title="Delete">
                    <IconButton size="small" color="error" onClick={() => handleDeleteRule(rule.id)}><DeleteIcon fontSize="small" /></IconButton>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Add/Edit Dialog */}
      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ fontWeight: 800 }}>{editingRule ? 'Edit Rule' : 'Create Custom Rule'}</DialogTitle>
        <DialogContent dividers>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, pt: 1 }}>
            <TextField 
              label="Column Name" 
              fullWidth 
              value={formData.column_name} 
              onChange={(e) => setFormData({...formData, column_name: e.target.value})} 
            />
            <TextField 
              select 
              label="Rule Type" 
              fullWidth 
              value={formData.rule_type} 
              onChange={(e) => setFormData({...formData, rule_type: e.target.value})}
            >
              <MenuItem value="not_null">Not Null</MenuItem>
              <MenuItem value="min_value">Min Value</MenuItem>
              <MenuItem value="max_value">Max Value</MenuItem>
              <MenuItem value="regex">Regex Match</MenuItem>
              <MenuItem value="custom">Custom Logic</MenuItem>
            </TextField>
            <TextField 
              label="Rule Expression" 
              fullWidth 
              multiline
              rows={2}
              placeholder="e.g., column > 0 or custom SQL expression"
              value={formData.rule_expression} 
              onChange={(e) => setFormData({...formData, rule_expression: e.target.value})} 
            />
            <FormControlLabel
              control={<Switch checked={formData.is_active} onChange={(e) => setFormData({...formData, is_active: e.target.checked})} />}
              label="Active immediately"
            />
          </Box>
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleSaveRule} sx={{ px: 4 }}>Save Rule</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Rules;