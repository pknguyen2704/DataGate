import React, { useState } from "react";
import {
  Box, Typography, Paper, Tabs, Tab, Button, TextField, MenuItem, Grid, Stack,
  FormControl, InputLabel, Select
} from "@mui/material";
import { Search, FilterList, Add } from "@mui/icons-material";
import { useParams } from "react-router-dom";
import { dataAssetsApi } from "~/apis/dataAssetsApi";
import { useApiResource } from "~/hooks/useApiResource";
import { useRBAC } from "~/rbac/useRBAC";
import { PermissionCode } from "~/rbac/permission";

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
  const { hasPermission } = useRBAC();
  const canManage = hasPermission(PermissionCode.THRESHOLD_MANAGE);

  // API Resources (only for schema check)
  const tableRes = useApiResource(() => dataAssetsApi.get(tableId), [tableId]);
  const isSilver = tableRes.data?.schema_name?.toLowerCase() === "silver";

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
    setAddTrigger(0);
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
          <Grid item xs={12} sm={6}>
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
          <Grid item xs={12} sm={6}>
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
