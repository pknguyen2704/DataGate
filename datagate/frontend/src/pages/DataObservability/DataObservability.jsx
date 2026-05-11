import React, { useState, useEffect } from "react";
import { 
  Grid, Stack, Typography, FormControl, InputLabel, Select, MenuItem, Box, Paper, Button 
} from "@mui/material";
import { RefreshOutlined } from "@mui/icons-material";
import { observabilityApi } from "~/apis/observabilityApi";
import { StateBox } from "~/components/DataGate/Page";
import { useApiResource } from "~/hooks/useApiResource";
import { format } from "date-fns";

const GRAFANA_DASHBOARD_URL = import.meta.env.VITE_GRAFANA_DASHBOARD_URL || "";

function DataObservability() {
  const tree = useApiResource(() => observabilityApi.managedTree());
  const variables = useApiResource(() => observabilityApi.grafanaVariables());
  const [selectedTable, setSelectedTable] = useState("");
  const [selectedTableId, setSelectedTableId] = useState("");
  const [selectedFullTableName, setSelectedFullTableName] = useState("");
  const [selectedFrom, setSelectedFrom] = useState("");
  const [selectedTo, setSelectedTo] = useState("");

  const loading = tree.loading || variables.loading;
  const error = tree.error || variables.error;

  const allTables = React.useMemo(() => {
    if (!tree.data) return [];
    return tree.data.flatMap(schema => 
      schema.tables.map(table => ({
        ...table,
        schema_name: schema.schema_name,
        full_name: `${schema.schema_name}.${table.table_name}`
      }))
    );
  }, [tree.data]);

  useEffect(() => {
    if (allTables.length > 0 && !selectedTableId) {
      const first = allTables[0];
      setSelectedTableId(first.table_id);
      setSelectedTable(first.table_name);
      setSelectedFullTableName(first.full_name);
    }
  }, [allTables, selectedTableId]);

  useEffect(() => {
    const hours = variables.data?.processing_date_hours || [];
    if (hours.length > 0 && !selectedFrom) {
      setSelectedFrom(hours[0]);
      setSelectedTo(hours[hours.length - 1]);
    }
  }, [variables.data, selectedFrom]);

  const handleTableChange = (e) => {
    const table = allTables.find(t => t.table_id === e.target.value);
    if (table) {
      setSelectedTableId(table.table_id);
      setSelectedTable(table.table_name);
      setSelectedFullTableName(table.full_name);
    }
  };

  const dashboardUrl = React.useMemo(() => {
    const baseUrl = GRAFANA_DASHBOARD_URL;
    if (!baseUrl || !selectedTableId || !selectedTable || !selectedFrom) return "";
    
    const fromEpoch = new Date(selectedFrom).getTime();
    const toEpoch = new Date(selectedTo || selectedFrom).getTime();

    const params = new URLSearchParams({
      orgId: "1",
      from: fromEpoch.toString(),
      to: toEpoch.toString(),
      timezone: "browser",
      "var-table_name": selectedTable,
      "var-table_id": selectedTableId,
      refresh: "1m",
      theme: "light",
      kiosk: "1"
    });
    return `${baseUrl}${baseUrl.includes('?') ? '&' : '?'}${params.toString()}`;
  }, [selectedFrom, selectedTo, selectedTable, selectedTableId]);

  return (
    <Box sx={{ p: { xs: 2, md: 3 }, bgcolor: "background.default", flexGrow: 1, overflow: "hidden" }}>
      <Stack spacing={3}>
        {/* Title Frame */}
        <Paper variant="outlined" sx={{ p: 2.5, borderRadius: 2, bgcolor: 'white', display: 'flex', justifyContent: 'space-between', alignItems: 'center', border: '1px solid', borderColor: 'divider', boxShadow: '0 2px 10px rgba(0,0,0,0.02)' }}>
          <Box>
            <Typography variant="h5" sx={{ fontWeight: 800, color: 'primary.main' }}>Observability</Typography>
            <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>Interactive monitoring view using embedded Grafana dashboards.</Typography>
          </Box>
          <Button startIcon={<RefreshOutlined />} variant="outlined" onClick={() => { tree.reload(); variables.reload(); }} sx={{ borderRadius: 1.5 }}>Refresh</Button>
        </Paper>

        {/* Filters Section */}
        <Paper variant="outlined" sx={{ p: 2.5, borderRadius: 2, bgcolor: 'white', border: '1px solid', borderColor: 'divider', boxShadow: '0 2px 10px rgba(0,0,0,0.02)' }}>
          <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} alignItems="center">
            <FormControl size="small" sx={{ minWidth: 300, bgcolor: 'white' }}>
              <InputLabel>Select Table</InputLabel>
              <Select value={selectedTableId} label="Select Table" onChange={handleTableChange}>
                {allTables.map(t => (
                  <MenuItem key={t.table_id} value={t.table_id}>{t.full_name}</MenuItem>
                ))}
              </Select>
            </FormControl>
            <FormControl size="small" sx={{ minWidth: 220, bgcolor: 'white' }}>
              <InputLabel>From</InputLabel>
              <Select value={selectedFrom} label="From" onChange={(e) => setSelectedFrom(e.target.value)}>
                {(variables.data?.processing_date_hours || []).map(h => (
                  <MenuItem key={h} value={h}>{format(new Date(h), "yyyy-MM-dd HH:mm:ss")}</MenuItem>
                ))}
              </Select>
            </FormControl>
            <FormControl size="small" sx={{ minWidth: 220, bgcolor: 'white' }}>
              <InputLabel>To</InputLabel>
              <Select value={selectedTo} label="To" onChange={(e) => setSelectedTo(e.target.value)}>
                {(variables.data?.processing_date_hours || []).map(h => (
                  <MenuItem key={h} value={h}>{format(new Date(h), "yyyy-MM-dd HH:mm:ss")}</MenuItem>
                ))}
              </Select>
            </FormControl>
            <Box sx={{ flexGrow: 1 }} />
            <Typography variant="body2" sx={{ fontWeight: 'bold', color: 'text.secondary' }}>
              Viewing: <span style={{ color: '#1E40AF' }}>{selectedFullTableName || '---'}</span>
            </Typography>
          </Stack>
        </Paper>

        <Box sx={{ width: "100%", height: 800, borderRadius: 2, overflow: "hidden", border: '1px solid', borderColor: 'divider', boxShadow: '0 10px 30px rgba(0,0,0,0.05)', bgcolor: 'white' }}>
          <StateBox loading={loading} error={error}>
            {dashboardUrl ? (
              <iframe title="Grafana" src={dashboardUrl} width="100%" height="100%" frameBorder="0" style={{ border: 0, display: 'block' }} />
            ) : (
              <Box sx={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', bgcolor: 'grey.50' }}>
                <Typography color="text.secondary">Please select a table and date range to view the dashboard.</Typography>
              </Box>
            )}
          </StateBox>
        </Box>
      </Stack>
    </Box>
  );
}

export default DataObservability;
