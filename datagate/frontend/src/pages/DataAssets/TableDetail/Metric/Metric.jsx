import React, { useState } from "react";
import {
  Box, Typography, Paper, Tabs, Tab, Button, TextField, MenuItem, Grid, Stack,
  FormControl, InputLabel, Select
} from "@mui/material";
import { Refresh, Search, FilterList, Add } from "@mui/icons-material";
import { useParams } from "react-router-dom";
import { dataAssetsApi } from "~/apis/dataAssetsApi";
import { useApiResource } from "~/hooks/useApiResource";
import { useSelector } from "react-redux";

// Sub-components
import Metadata from "./Metadata/Metadata";
import Profiling from "./Profiling/Profiling";
import AnomalyDetection from "./AnomalyDetection/AnomalyDetection";

const Metric = () => {
  const { tableId } = useParams();
  const [activeTab, setActiveTab] = useState(0);
  const [searchQuery, setSearchQuery] = useState("");
  const [filters, setFilters] = useState({
    status: "",
    severity: ""
  });
  const [addTrigger, setAddTrigger] = useState(0); // Counter to trigger add in children
  const { user } = useSelector(state => state.auth);

  // Check permission: threshold:update
  const isAdmin = user?.roles?.some(r => r === "Admin" || r?.name === "Admin");
  const hasThresholdPerm = user?.permissions?.some(p => p === "threshold:update" || p?.code === "threshold:update");
  const canManage = isAdmin || hasThresholdPerm;

  // API Resources (only for schema check)
  const tableRes = useApiResource(() => dataAssetsApi.get(tableId), [tableId]);
  const isSilver = tableRes.data?.schema_name?.toLowerCase() === "silver";

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Tabs value={activeTab} onChange={handleTabChange} sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tab label="Table Metadata" />
          <Tab label="Column Profiling" />
          {isSilver && <Tab label="Anomaly Thresholds" />}
        </Tabs>
        <Stack direction="row" spacing={1}>
          <Button startIcon={<Refresh />} size="small" onClick={() => window.location.reload()}>Refresh</Button>
          {canManage && (
            <Button 
              variant="contained" 
              startIcon={<Add />} 
              size="small"
              onClick={() => setAddTrigger(prev => prev + 1)}
            >
              Add Metric
            </Button>
          )}
        </Stack>
      </Box>

      {/* Filter Bar */}
      <Paper variant="outlined" sx={{ p: 2, mb: 2, borderRadius: 2, bgcolor: 'background.default' }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              size="small"
              placeholder="Search by metric, column, description..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              InputProps={{
                startAdornment: <Search fontSize="small" sx={{ mr: 1, color: 'text.secondary' }} />,
              }}
            />
          </Grid>
          <Grid item xs={12} md={2}>
            {/* Placeholder to match Rules layout spacing */}
          </Grid>
          <Grid item xs={12} md={2}>
            <FormControl fullWidth size="small">
              <InputLabel>Status</InputLabel>
              <Select
                label="Status"
                value={filters.status}
                onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value }))}
              >
                <MenuItem value="">All Status</MenuItem>
                <MenuItem value="active">Active</MenuItem>
                <MenuItem value="inactive">Inactive</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={2}>
            <FormControl fullWidth size="small">
              <InputLabel>Severity</InputLabel>
              <Select
                label="Severity"
                value={filters.severity}
                onChange={(e) => setFilters(prev => ({ ...prev, severity: e.target.value }))}
              >
                <MenuItem value="">All Severities</MenuItem>
                <MenuItem value="warning">Warning</MenuItem>
                <MenuItem value="critical">Critical</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={2}>
            <Button 
              fullWidth 
              variant="contained" 
              startIcon={<FilterList />}
              sx={{ 
                bgcolor: 'primary.main', 
                color: 'white',
                '&:hover': { bgcolor: 'primary.dark' },
                fontWeight: 700,
                borderRadius: 1.5
              }}
            >
              Filter
            </Button>
          </Grid>
        </Grid>
      </Paper>

      <Paper variant="outlined" sx={{ borderRadius: 2, overflow: 'hidden' }}>
        {activeTab === 0 && (
          <Metadata 
            tableId={tableId} 
            canManage={canManage} 
            searchQuery={searchQuery} 
            filters={filters} 
            addTrigger={addTrigger}
          />
        )}
        {activeTab === 1 && (
          <Profiling 
            tableId={tableId} 
            canManage={canManage} 
            searchQuery={searchQuery} 
            filters={filters} 
            addTrigger={addTrigger}
          />
        )}
        {activeTab === 2 && isSilver && (
          <AnomalyDetection 
            tableId={tableId} 
            canManage={canManage} 
            searchQuery={searchQuery} 
            filters={filters} 
            addTrigger={addTrigger}
          />
        )}
      </Paper>
    </Box>
  );
};

export default Metric;