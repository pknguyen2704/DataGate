import React, { useState } from "react";
import { 
  Grid, Typography, Box, FormControl, InputLabel, Select, MenuItem, Stack, Paper,
  Table, TableBody, TableCell, TableHead, TableRow 
} from "@mui/material";
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, 
} from "recharts";
import { Panel, Stat, StateBox, StatusChip } from "~/components/DataGate/Page";
import { healthApi } from "~/apis/healthApi";
import { useApiResource } from "~/hooks/useApiResource";
import { format } from "date-fns";

function Home() {
  const [selectedSchema, setSelectedSchema] = useState("all");
  const overview = useApiResource(() => healthApi.overview({ schema_name: selectedSchema !== "all" ? selectedSchema : undefined }), [selectedSchema]);
  const timelineData = useApiResource(() => healthApi.timeline({ schema_name: selectedSchema !== "all" ? selectedSchema : undefined }), [selectedSchema]);
  const tableHealths = useApiResource(() => healthApi.tables(), []);
  
  const stats = overview.data || {};
  const timeline = timelineData.data || [];
  const tables = tableHealths.data || [];

  const filteredTables = selectedSchema === "all" ? tables : tables.filter(t => t.schema_name === selectedSchema);

  return (
    <Box sx={{ p: { xs: 2, md: 3 }, bgcolor: "background.default", flexGrow: 1, overflow: "hidden" }}>
      <Stack spacing={3}>
        {/* Title Frame */}
        <Paper variant="outlined" sx={{ p: 2.5, borderRadius: 2, bgcolor: 'white', display: 'flex', justifyContent: 'space-between', alignItems: 'center', border: '1px solid', borderColor: 'divider', boxShadow: '0 2px 10px rgba(0,0,0,0.02)' }}>
          <Box>
            <Typography variant="h5" sx={{ fontWeight: 800, color: 'primary.main' }}>Platform Health Overview</Typography>
            <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>Comprehensive observability across all monitored data sources.</Typography>
          </Box>
          <FormControl size="small" sx={{ minWidth: 200, bgcolor: 'white', borderRadius: 1.5 }}>
            <InputLabel>Filter by Schema</InputLabel>
            <Select 
              value={selectedSchema} 
              label="Filter by Schema"
              onChange={(e) => setSelectedSchema(e.target.value)}
              sx={{ borderRadius: 1.5 }}
            >
              <MenuItem value="all">All Schemas (Global)</MenuItem>
              {/* Unique schemas from tables list */}
              {Array.from(new Set(tables.map(t => t.schema_name))).map(s => <MenuItem key={s} value={s}>{s}</MenuItem>)}
            </Select>
          </FormControl>
        </Paper>

        {/* Statistics Section */}
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Stat 
              label="Monitored Tables" 
              value={stats.total_tables} 
              subtitle="Total unique tables registered in platform"
              tone="blue"
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <Stat 
              label="Latest Batch Processing" 
              value={stats.latest_batch ? format(new Date(stats.latest_batch), "yyyy-MM-dd HH:mm:ss") : null} 
              subtitle={stats.latest_batch ? "Timestamp of the most recent data quality batch" : "No batches processed"}
              tone="amber"
            />
          </Grid>
        </Grid>

        {/* Timeline Section */}
        <Panel 
          title="Verification Result Timeline" 
          subtitle="Real-time status of data quality checks by processing hour."
        >
          <StateBox loading={timelineData.loading} error={timelineData.error} empty={!timeline.length}>
            <Box sx={{ height: 350, mt: 2 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={timeline} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                  <XAxis 
                    dataKey="processing_date_hour" 
                    tickFormatter={(val) => format(new Date(val), "MM-dd HH:mm")}
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
