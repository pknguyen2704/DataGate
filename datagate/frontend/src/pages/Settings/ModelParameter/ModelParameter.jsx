import React, { useState, useEffect } from "react";
import {
  Box,
  Button,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  Typography,
  Paper,
  TextField,
  CircularProgress
} from "@mui/material";
import { UploadFileOutlined, SaveOutlined, RestartAltOutlined } from "@mui/icons-material";
import { observabilityApi } from "~/apis/observabilityApi";
import { lightgbmApi } from "~/apis/lightgbmApi";
import { useApiResource } from "~/hooks/useApiResource";
import { toast } from "react-toastify";

function ModelParameter() {
  const tree = useApiResource(() => observabilityApi.managedTree());
  const [selectedTableId, setSelectedTableId] = useState("");
  const [selectedTableName, setSelectedTableName] = useState("");
  const [editingId, setEditingId] = useState(null);
  const [jsonConfig, setJsonConfig] = useState("");
  const [originalConfig, setOriginalConfig] = useState("");
  const [loadingConfig, setLoadingConfig] = useState(false);
  const [saving, setSaving] = useState(false);

  const schemas = tree.data || [];
  const allTables = React.useMemo(() => 
    schemas.flatMap(s => s.tables.map(t => ({ ...t, full_name: `${s.schema_name}.${t.table_name}` }))),
    [schemas]
  );

  useEffect(() => {
    if (allTables.length > 0 && !selectedTableId) {
      handleTableSelect(allTables[0].table_id, allTables[0].full_name);
    }
  }, [allTables]);

  const handleTableSelect = async (id, name) => {
    setSelectedTableId(id);
    setSelectedTableName(name);
    setLoadingConfig(true);
    setEditingId(null);
    try {
      const res = await lightgbmApi.tableParameters(id);
      if (res.data) {
        setEditingId(res.data.id);
        const jsonStr = JSON.stringify(res.data, null, 2);
        setJsonConfig(jsonStr);
        setOriginalConfig(jsonStr);
      } else {
        setJsonConfig("{\n  \"learning_rate\": 0.05,\n  \"num_leaves\": 31\n}");
        setOriginalConfig("");
      }
    } catch (err) {
      setJsonConfig("{\n  \"learning_rate\": 0.05,\n  \"num_leaves\": 31\n}");
      setOriginalConfig("");
    } finally {
      setLoadingConfig(false);
    }
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const parsed = JSON.parse(event.target.result);
        setJsonConfig(JSON.stringify(parsed, null, 2));
      } catch (err) {
        toast.error("Invalid JSON file");
      }
    };
    reader.readAsText(file);
    e.target.value = null; // reset input
  };

  const handleSave = async () => {
    let parsed;
    try {
      parsed = JSON.parse(jsonConfig);
    } catch (err) {
      toast.error("Invalid JSON format");
      return;
    }
    
    setSaving(true);
    try {
      if (editingId) {
        await lightgbmApi.update(editingId, parsed);
        toast.success("Parameters updated successfully");
      } else {
        await lightgbmApi.create({ table_id: selectedTableId, ...parsed });
        toast.success("Parameters created successfully");
        // Re-fetch to get the new ID
        handleTableSelect(selectedTableId, selectedTableName);
      }
      setOriginalConfig(jsonConfig);
    } catch (err) {
      toast.error("Failed to save parameters");
    } finally {
      setSaving(false);
    }
  };

  if (tree.loading) {
    return <Box sx={{ display: 'flex', justifyContent: 'center', p: 5 }}><CircularProgress /></Box>;
  }

  return (
    <Box sx={{ p: { xs: 2, md: 3 } }}>
      <Stack spacing={3}>
        <Paper variant="outlined" sx={{ p: 2.5, borderRadius: 2, bgcolor: 'white', display: 'flex', justifyContent: 'space-between', alignItems: 'center', border: '1px solid', borderColor: 'divider', boxShadow: '0 2px 10px rgba(0,0,0,0.02)' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 3 }}>
            <Typography variant="h6" fontWeight="bold">Model Parameters</Typography>
            <FormControl size="small" sx={{ minWidth: 350, bgcolor: 'white' }}>
              <InputLabel>Target Table</InputLabel>
              <Select 
                value={selectedTableId} 
                label="Target Table"
                onChange={(e) => {
                  const table = allTables.find(t => t.table_id === e.target.value);
                  handleTableSelect(table.table_id, table.full_name);
                }}
              >
                {allTables.map(t => (
                  <MenuItem key={t.table_id} value={t.table_id}>{t.full_name}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>
        </Paper>

        <Paper variant="outlined" sx={{ borderRadius: 2, overflow: 'hidden', bgcolor: 'white', border: '1px solid', borderColor: 'divider', boxShadow: '0 4px 20px rgba(0,0,0,0.03)' }}>
          <Box sx={{ p: 2.5, borderBottom: '1px solid', borderColor: 'divider', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="subtitle1" fontWeight="bold" color="primary">
              JSON Configuration for <span style={{ color: '#1E40AF' }}>{selectedTableName || "..." }</span>
            </Typography>
            <Button component="label" startIcon={<UploadFileOutlined />} size="small" variant="outlined" sx={{ borderRadius: 1.5 }}>
              Upload JSON
              <input type="file" accept=".json" hidden onChange={handleFileUpload} />
            </Button>
          </Box>
          <Box sx={{ p: 0, position: 'relative', bgcolor: '#F8FAFC' }}>
            {loadingConfig && (
              <Box sx={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, display: 'flex', justifyContent: 'center', alignItems: 'center', bgcolor: 'rgba(255,255,255,0.7)', zIndex: 10 }}>
                <CircularProgress />
              </Box>
            )}
            <TextField
              multiline
              fullWidth
              minRows={18}
              value={jsonConfig}
              onChange={(e) => setJsonConfig(e.target.value)}
              variant="standard"
              InputProps={{
                disableUnderline: true,
                sx: { 
                  fontFamily: '"Fira Code", "Roboto Mono", monospace', 
                  p: 3, 
                  fontSize: '0.875rem',
                  lineHeight: 1.6,
                  color: '#334155'
                }
              }}
            />
          </Box>
          <Box sx={{ p: 2.5, borderTop: '1px solid', borderColor: 'divider', display: 'flex', justifyContent: 'flex-end', gap: 2, bgcolor: 'white' }}>
            <Button 
              variant="outlined" 
              startIcon={<RestartAltOutlined />}
              onClick={() => setJsonConfig(originalConfig)}
              sx={{ borderRadius: 1.5 }}
            >
              Reset
            </Button>
            <Button 
              variant="contained" 
              startIcon={<SaveOutlined />}
              onClick={handleSave}
              disabled={saving || !selectedTableId}
              sx={{ borderRadius: 1.5, px: 4 }}
            >
              {saving ? 'Saving...' : editingId ? 'Update Parameters' : 'Save Parameters'}
            </Button>
          </Box>
        </Paper>
      </Stack>
    </Box>
  );
}

export default ModelParameter;