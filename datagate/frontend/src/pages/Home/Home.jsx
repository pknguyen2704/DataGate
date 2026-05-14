import React, { useState } from "react";
import { 
  Typography, Box, FormControl, InputLabel, Select, MenuItem, Stack, Paper,
  Table, TableBody, TableCell, TableHead, TableRow, TextField, Button
} from "@mui/material";
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, 
} from "recharts";
import { Panel, Stat, StateBox, StatusChip } from "~/components/DataGate/Page";
import { homeApi } from "~/apis/homeApi";
import { useApiResource } from "~/hooks/useApiResource";
import { format } from "date-fns";

function Home() {
  const [selectedSchema, setSelectedSchema] = useState("all");
  const [timelineRange, setTimelineRange] = useState({ from: "", to: "" });
  
  const summaryRes = useApiResource(() => homeApi.summary({ 
    schema_name: selectedSchema !== "all" ? selectedSchema : undefined 
  }), [selectedSchema]);
  
  const timelineData = useApiResource(() => homeApi.timeline({ 
    schema_name: selectedSchema !== "all" ? selectedSchema : undefined,
    from_time: timelineRange.from || undefined,
    to_time: timelineRange.to || undefined
  }), [selectedSchema, timelineRange]);
  
  const tableHealths = useApiResource(() => homeApi.tableHealths(), []);
  
  const summary = summaryRes.data || { total_tables: 0, total_pass: 0, total_fail: 0, warning_fail: 0, critical_fail: 0, unresolved_alerts: 0 };
  const timeline = timelineData.data || [];
  const tables = tableHealths.data || [];

  const filteredTables = selectedSchema === "all" ? tables : tables.filter(t => t.schema_name === selectedSchema);

  return (
    <Box sx={{ p: { xs: 2, md: 3 }, bgcolor: "background.default", flexGrow: 1, overflow: "auto", display: 'flex', flexDirection: 'column', minWidth: 0 }}>
      <Stack spacing={3} sx={{ width: '100%' }}>
        {/* Title Frame */}
        <Paper variant="outlined" sx={{ p: 2.5, borderRadius: 2, bgcolor: 'white', display: 'flex', justifyContent: 'space-between', alignItems: 'center', border: '1px solid', borderColor: 'divider', boxShadow: '0 2px 10px rgba(0,0,0,0.02)' }}>
          <Box>
            <Typography variant="h5" sx={{ fontWeight: 800, color: 'primary.main' }}>Platform Health Summary</Typography>
            <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>Comprehensive observability across all monitored data sources.</Typography>
          </Box>
          <FormControl size="small" sx={{ minWidth: 200, flexShrink: 0, bgcolor: 'white', borderRadius: 1.5 }}>
            <InputLabel>Filter by Schema</InputLabel>
            <Select 
              value={selectedSchema} 
              label="Filter by Schema"
              onChange={(e) => setSelectedSchema(e.target.value)}
              sx={{ borderRadius: 1.5 }}
            >
              <MenuItem value="all">All Schemas</MenuItem>
              {Array.from(new Set(tables.map(t => t.schema_name))).map(s => <MenuItem key={s} value={s}>{s}</MenuItem>)}
            </Select>
          </FormControl>
        </Paper>

        {/* Statistics Section */}
        <Box sx={{ 
          display: 'grid', 
          gridTemplateColumns: { 
            xs: '1fr', 
            sm: 'repeat(3, 1fr)', 
            md: 'repeat(6, 1fr)' 
          }, 
          gap: 2,
          width: '100%'
        }}>
          <Stat label="Monitored Tables" value={summary.total_tables} tone="blue" />
          <Stat label="Total Pass" value={summary.total_pass} tone="green" />
          <Stat label="Total Fail" value={summary.total_fail} tone="red" />
          <Stat label="Warning Fail" value={summary.warning_fail} tone="amber" />
          <Stat label="Critical Fail" value={summary.critical_fail} tone="red" />
          <Stat label="Unresolved Alerts" value={summary.unresolved_alerts} tone="amber" />
        </Box>

        {/* Timeline Section */}
        <Panel 
          title="Verification Result Timeline" 
          subtitle="Real-time status of data quality checks by processing hour."
          action={
            <Stack direction="row" spacing={1}>
              <TextField 
                size="small" type="datetime-local" label="From" 
                InputLabelProps={{ shrink: true }}
                inputProps={{ step: 1 }}
                value={timelineRange.from}
                onChange={e => setTimelineRange(prev => ({ ...prev, from: e.target.value }))}
                sx={{ width: 220 }}
              />
              <TextField 
                size="small" type="datetime-local" label="To" 
                InputLabelProps={{ shrink: true }}
                inputProps={{ step: 1 }}
                value={timelineRange.to}
                onChange={e => setTimelineRange(prev => ({ ...prev, to: e.target.value }))}
                sx={{ width: 220 }}
              />
              <Button size="small" onClick={() => setTimelineRange({ from: "", to: "" })}>Reset</Button>
            </Stack>
          }
        >
          <StateBox loading={timelineData.loading} error={timelineData.error} empty={!timeline.length}>
            <Box sx={{ height: 350, mt: 2, width: '100%', minWidth: 0 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={timeline} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                  <XAxis 
                    dataKey="processing_date_hour" 
                    tickFormatter={(val) => format(new Date(val), "MM-dd HH:mm:ss")}
                    stroke="#94A3B8"
                    fontSize={12}
                    tickMargin={10}
                  />
                  <YAxis stroke="#94A3B8" fontSize={12} />
                  <Tooltip 
                    contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)' }}
                    labelFormatter={(label) => format(new Date(label), "yyyy-MM-dd HH:mm:ss")}
                  />
                  <Legend verticalAlign="top" align="right" wrapperStyle={{ paddingBottom: 20 }} />
                  <Bar dataKey="fail_critical" name="Fail (Critical)" stackId="a" fill="#EF4444" radius={[0, 0, 0, 0]} />
                  <Bar dataKey="fail_warning" name="Fail (Warning)" stackId="a" fill="#F59E0B" />
                  <Bar dataKey="pass_critical" name="Pass (Critical)" stackId="a" fill="#10B981" />
                  <Bar dataKey="pass_warning" name="Pass (Warning)" stackId="a" fill="#34D399" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </Box>
          </StateBox>
        </Panel>
      </Stack>
    </Box>
  );
}

export default Home;
