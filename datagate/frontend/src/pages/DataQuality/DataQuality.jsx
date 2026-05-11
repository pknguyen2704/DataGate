import React, { useState, useEffect } from "react";
import { 
  Box, Button, Table, TableBody, TableCell, TableHead, TableRow, 
  Typography, Paper, CircularProgress, FormControl, Select, MenuItem, 
  InputLabel, Stack, Grid 
} from "@mui/material";
import { RefreshOutlined } from "@mui/icons-material";
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, 
  ResponsiveContainer, Cell 
} from "recharts";
import { format } from "date-fns";
import { qualityApi } from "~/apis/qualityApi";
import { anomalyApi } from "~/apis/anomalyApi";
import { observabilityApi } from "~/apis/observabilityApi";
import { StateBox, StatusChip, TabContainer, TabButton } from "~/components/DataGate/Page";
import { useApiResource } from "~/hooks/useApiResource";

const tabs = [
  { value: "overall", label: "Overall Verify Results" },
  { value: "metadata", label: "Metadata Verify" },
  { value: "profiling", label: "Profiling Verify" },
  { value: "rules", label: "Rule Verify" },
  { value: "anomaly", label: "Anomaly Detection" },
];

const checkTypes = ["all", "metadata", "profiling", "anomaly", "rule"];
const severities = ["all", "critical", "warning"];
const statuses = ["all", "pass", "fail"];

function DataQuality() {
  const tree = useApiResource(() => observabilityApi.managedTree());
  const variables = useApiResource(() => observabilityApi.grafanaVariables());
  const [selectedTableId, setSelectedTableId] = useState("");
  const [selectedTableName, setSelectedTableName] = useState("");
  const [tab, setTab] = useState("overall");

  const [filterType, setFilterType] = useState("all");
  const [filterStatus, setFilterStatus] = useState("all");
  const [filterSeverity, setFilterSeverity] = useState("all");
  const [filterResolved, setFilterResolved] = useState("all");

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

  const filteredTablesByTab = React.useMemo(() => {
    if (tab === "rules") {
      return allTables.filter(t => ["silver", "gold"].includes(t.schema_name.toLowerCase()));
    }
    if (tab === "anomaly") {
      return allTables.filter(t => t.schema_name.toLowerCase() === "silver");
    }
    return allTables;
  }, [allTables, tab]);

  useEffect(() => {
    if (filteredTablesByTab.length > 0) {
      const exists = filteredTablesByTab.find(t => t.table_id === selectedTableId);
      if (!exists) {
        const first = filteredTablesByTab[0];
        setSelectedTableId(first.table_id);
        setSelectedTableName(first.full_name);
      }
    } else {
      setSelectedTableId("");
      setSelectedTableName("");
    }
  }, [filteredTablesByTab, selectedTableId]);

  const results = useApiResource(() => qualityApi.results({ 
    table_id: selectedTableId,
    result_type: tab !== "overall" && tab !== "anomaly" ? (tab === "rules" ? "rule" : tab) : (filterType !== "all" ? filterType : undefined),
    unresolved_only: filterResolved === "unresolved" ? true : undefined
  }), [selectedTableId, tab, filterType, filterResolved]);

  const aucTimeline = useApiResource(() => {
    if (selectedTableId && tab === "anomaly") {
      return anomalyApi.aucTimeline(selectedTableId);
    }
    return Promise.resolve({ data: [] });
  }, [selectedTableId, tab]);

  const [shapData, setShapData] = useState([]);
  const [loadingShap, setLoadingShap] = useState(false);

  useEffect(() => {
    const fetchShap = async () => {
      const latestAuc = aucTimeline.data?.[0];
      if (latestAuc && tab === "anomaly") {
        setLoadingShap(true);
        try {
          const res = await anomalyApi.shap(latestAuc.id);
          setShapData(res.data || []);
        } catch (err) {
          setShapData([]);
        } finally {
          setLoadingShap(false);
        }
      } else {
        setShapData([]);
      }
    };
    fetchShap();
  }, [aucTimeline.data, tab]);

  const refresh = () => {
    tree.reload();
    variables.reload();
    results.reload();
    if (tab === "anomaly") aucTimeline.reload();
  };

  const handleTableChange = (e) => {
    const table = allTables.find(t => t.table_id === e.target.value);
    if (table) {
      setSelectedTableId(table.table_id);
      setSelectedTableName(table.full_name);
    }
  };

  let filteredRows = results.data || [];
  if (filterStatus !== "all") {
    filteredRows = filteredRows.filter(r => r.status === filterStatus);
  }
  if (filterSeverity !== "all") {
    filteredRows = filteredRows.filter(r => r.severity_level === filterSeverity);
  }
  if (filterResolved === "resolved") {
    filteredRows = filteredRows.filter(r => r.is_resolved === true);
  }

  return (
    <Box sx={{ p: { xs: 2, md: 3 }, bgcolor: "background.default", flexGrow: 1, overflow: "hidden" }}>
      <Stack spacing={3}>
        {/* Title Frame */}
        <Paper variant="outlined" sx={{ p: 2.5, borderRadius: 2, bgcolor: 'white', display: 'flex', justifyContent: 'space-between', alignItems: 'center', border: '1px solid', borderColor: 'divider', boxShadow: '0 2px 10px rgba(0,0,0,0.02)' }}>
          <Box>
            <Typography variant="h5" sx={{ fontWeight: 800, color: 'primary.main' }}>Data Quality</Typography>
            <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>Centralized view of data quality verifications and anomalies.</Typography>
          </Box>
          <Button startIcon={<RefreshOutlined />} variant="outlined" onClick={refresh}>Refresh</Button>
        </Paper>

        {/* Global Filter Panel */}
        <Paper variant="outlined" sx={{ p: 2.5, borderRadius: 2, bgcolor: 'white', border: '1px solid', borderColor: 'divider', boxShadow: '0 2px 10px rgba(0,0,0,0.02)' }}>
          <Stack direction={{ xs: 'column', md: 'row' }} spacing={3} alignItems="center">
            <FormControl size="small" sx={{ minWidth: 300, bgcolor: 'white' }}>
              <InputLabel>Table Source</InputLabel>
              <Select value={selectedTableId} label="Table Source" onChange={handleTableChange}>
                {filteredTablesByTab.map(t => (
                  <MenuItem key={t.table_id} value={t.table_id}>{t.full_name}</MenuItem>
                ))}
              </Select>
            </FormControl>
            <TabContainer sx={{ mb: 0, p: 0.5, bgcolor: 'grey.100' }}>
              {tabs.map((t) => (
                <TabButton
                  key={t.value}
                  active={t.value === tab}
                  label={t.label}
                  onClick={() => setTab(t.value)}
                />
              ))}
            </TabContainer>
          </Stack>
        </Paper>

        <Paper variant="outlined" sx={{ borderRadius: 2, overflow: 'hidden', bgcolor: 'white', border: '1px solid', borderColor: 'divider', boxShadow: '0 4px 20px rgba(0,0,0,0.03)' }}>
          <Box sx={{ p: 2.5, borderBottom: '1px solid', borderColor: 'divider' }}>
            <Typography variant="h6" fontWeight="bold">
              {tabs.find((t) => t.value === tab)?.label} - <span style={{ color: '#1E40AF' }}>{selectedTableName}</span>
            </Typography>
            
            {tab === "overall" && (
              <Paper variant="outlined" sx={{ p: 2, mt: 2, bgcolor: 'grey.50', borderRadius: 2, border: '1px solid', borderColor: 'divider' }}>
                <Stack direction="row" spacing={2} flexWrap="wrap" gap={1}>
                  <FormControl size="small" sx={{ minWidth: 120, bgcolor: 'white' }}>
                    <InputLabel>Type</InputLabel>
                    <Select value={filterType} label="Type" onChange={e => setFilterType(e.target.value)}>
                      {checkTypes.map(t => <MenuItem key={t} value={t}>{t}</MenuItem>)}
                    </Select>
                  </FormControl>
                  <FormControl size="small" sx={{ minWidth: 120, bgcolor: 'white' }}>
                    <InputLabel>Status</InputLabel>
                    <Select value={filterStatus} label="Status" onChange={e => setFilterStatus(e.target.value)}>
                      {statuses.map(t => <MenuItem key={t} value={t}>{t}</MenuItem>)}
                    </Select>
                  </FormControl>
                  <FormControl size="small" sx={{ minWidth: 120, bgcolor: 'white' }}>
                    <InputLabel>Severity</InputLabel>
                    <Select value={filterSeverity} label="Severity" onChange={e => setFilterSeverity(e.target.value)}>
                      {severities.map(t => <MenuItem key={t} value={t}>{t}</MenuItem>)}
                    </Select>
                  </FormControl>
                  <FormControl size="small" sx={{ minWidth: 120, bgcolor: 'white' }}>
                    <InputLabel>Resolution</InputLabel>
                    <Select value={filterResolved} label="Resolution" onChange={e => setFilterResolved(e.target.value)}>
                      <MenuItem value="all">All</MenuItem>
                      <MenuItem value="resolved">Resolved</MenuItem>
                      <MenuItem value="unresolved">Unresolved</MenuItem>
                    </Select>
                  </FormControl>
                </Stack>
              </Paper>
            )}
          </Box>
          
          <Box sx={{ overflowX: 'auto' }}>
            {tab === "overall" && (
              <StateBox loading={results.loading} error={results.error} empty={!filteredRows.length}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell sx={{ bgcolor: '#1E40AF !important', color: 'white !important', fontWeight: 'bold', py: 2 }}>Type</TableCell>
                      <TableCell sx={{ bgcolor: '#1E40AF !important', color: 'white !important', fontWeight: 'bold', py: 2 }}>Metric</TableCell>
                      <TableCell sx={{ bgcolor: '#1E40AF !important', color: 'white !important', fontWeight: 'bold', py: 2 }}>Status</TableCell>
                      <TableCell sx={{ bgcolor: '#1E40AF !important', color: 'white !important', fontWeight: 'bold', py: 2 }}>Severity</TableCell>
                      <TableCell sx={{ bgcolor: '#1E40AF !important', color: 'white !important', fontWeight: 'bold', py: 2 }}>Resolved</TableCell>
                      <TableCell sx={{ bgcolor: '#1E40AF !important', color: 'white !important', fontWeight: 'bold', py: 2 }}>Processing Hour</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {filteredRows.map((row) => (
                      <TableRow key={`${row.result_type}-${row.id}`} hover sx={{ '&:last-child td, &:last-child th': { border: 0 } }}>
                        <TableCell sx={{ textTransform: 'capitalize', fontWeight: 500 }}>{row.result_type}</TableCell>
                        <TableCell>{row.metric_name || row.constraint_name || "-"}</TableCell>
                        <TableCell><StatusChip value={row.status} /></TableCell>
                        <TableCell><StatusChip value={row.severity_level || "none"} /></TableCell>
                        <TableCell>{row.is_resolved ? "Yes" : "No"}</TableCell>
                        <TableCell>{format(new Date(row.processing_date_hour), "yyyy-MM-dd HH:mm:ss")}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </StateBox>
            )}

            {tab === "anomaly" && (
              <Box sx={{ p: 3 }}>
                <StateBox loading={aucTimeline.loading} error={aucTimeline.error} empty={!aucTimeline.data?.length}>
                  {aucTimeline.data?.[0] && (() => {
                    const latestAuc = aucTimeline.data[0];
                    const verifyResult = filteredRows.find(r => r.result_type === "anomaly" && r.processing_date_hour === latestAuc.processing_date_hour);
                    
                    return (
                      <Grid container spacing={4}>
                        <Grid item xs={12} md={4}>
                          <Paper variant="outlined" sx={{ p: 4, textAlign: 'center', bgcolor: '#F8FAFC', borderRadius: 3, border: '1px solid', borderColor: 'divider' }}>
                            <Typography variant="subtitle1" color="text.secondary" gutterBottom sx={{ fontWeight: 600 }}>
                              Latest AUC Score
                            </Typography>
                            <Typography variant="h2" fontWeight="900" sx={{ mb: 1, color: 'primary.main', letterSpacing: -1 }}>
                              {latestAuc.auc_score != null ? latestAuc.auc_score.toFixed(4) : "N/A"}
                            </Typography>
                            <StatusChip value={verifyResult?.status || "Unknown"} />
                            <Typography variant="body2" sx={{ mt: 3, color: 'text.secondary', fontWeight: 500 }}>
                              Batch: {format(new Date(latestAuc.processing_date_hour), 'yyyy-MM-dd HH:mm:ss')}
                            </Typography>
                          </Paper>
                        </Grid>
                        <Grid item xs={12} md={8}>
                          <Typography variant="h6" fontWeight="bold" gutterBottom sx={{ mb: 2 }}>
                            Feature Effects (SHAP)
                          </Typography>
                          {loadingShap ? (
                            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}><CircularProgress size={32} /></Box>
                          ) : shapData.length === 0 ? (
                            <Typography color="text.secondary">No SHAP data available for this batch.</Typography>
                          ) : (
                            <Box sx={{ height: 400, width: '100%', mt: 2 }}>
                              <ResponsiveContainer width="100%" height="100%">
                                <BarChart
                                  layout="vertical"
                                  data={[...shapData].sort((a, b) => (b.shap_score || 0) - (a.shap_score || 0)).slice(0, 10)}
                                  margin={{ left: 60, right: 30, top: 0, bottom: 0 }}
                                >
                                  <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                                  <XAxis type="number" hide />
                                  <YAxis 
                                    dataKey="feature_name" 
                                    type="category" 
                                    width={120} 
                                    tick={{ fontSize: 12, fontWeight: 600 }}
                                    axisLine={{ stroke: '#E2E8F0' }}
                                    tickLine={false}
                                  />
                                  <RechartsTooltip 
                                    cursor={{ fill: '#F1F5F9' }}
                                    contentStyle={{ borderRadius: 8, border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}
                                  />
                                  <Bar dataKey="shap_score" radius={[0, 4, 4, 0]}>
                                    {shapData.map((entry, index) => (
                                      <Cell key={`cell-${index}`} fill="#3B82F6" />
                                    ))}
                                  </Bar>
                                </BarChart>
                              </ResponsiveContainer>
                            </Box>
                          )}
                        </Grid>
                      </Grid>
                    );
                  })()}
                </StateBox>
              </Box>
            )}

            {["metadata", "profiling", "rules"].includes(tab) && (
              <StateBox loading={results.loading} error={results.error} empty={!filteredRows.length}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell sx={{ bgcolor: '#1E40AF !important', color: 'white !important', fontWeight: 'bold', py: 2 }}>Metric / Rule</TableCell>
                      <TableCell sx={{ bgcolor: '#1E40AF !important', color: 'white !important', fontWeight: 'bold', py: 2 }}>Column</TableCell>
                      <TableCell sx={{ bgcolor: '#1E40AF !important', color: 'white !important', fontWeight: 'bold', py: 2 }}>Status</TableCell>
                      <TableCell sx={{ bgcolor: '#1E40AF !important', color: 'white !important', fontWeight: 'bold', py: 2 }}>Severity</TableCell>
                      <TableCell sx={{ bgcolor: '#1E40AF !important', color: 'white !important', fontWeight: 'bold', py: 2 }}>Resolved</TableCell>
                      <TableCell sx={{ bgcolor: '#1E40AF !important', color: 'white !important', fontWeight: 'bold', py: 2 }}>Processing Hour</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {filteredRows.map((row) => (
                      <TableRow key={`${row.result_type}-${row.id}`} hover sx={{ '&:last-child td, &:last-child th': { border: 0 } }}>
                        <TableCell sx={{ fontWeight: 500 }}>{row.metric_name || row.constraint_name || "-"}</TableCell>
                        <TableCell>{row.column_name || "-"}</TableCell>
                        <TableCell><StatusChip value={row.status} /></TableCell>
                        <TableCell><StatusChip value={row.severity_level || "none"} /></TableCell>
                        <TableCell>{row.is_resolved ? "Yes" : "No"}</TableCell>
                        <TableCell>{format(new Date(row.processing_date_hour), "yyyy-MM-dd HH:mm:ss")}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </StateBox>
            )}
          </Box>
        </Paper>
      </Stack>
    </Box>
  );
}

export default DataQuality;
