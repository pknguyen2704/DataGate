import React, { useCallback, useEffect, useMemo, useState } from "react";
import {
  Alert,
  Avatar,
  Box,
  Button,
  Chip,
  CircularProgress,
  IconButton,
  InputAdornment,
  List,
  ListItemButton,
  ListItemText,
  Paper,
  Divider,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import {
  AccountCircleOutlined as OwnerIcon,
  ChevronRight as ChevronRightIcon,
  ExpandMore as ExpandMoreIcon,
  Refresh as RefreshIcon,
  Search as SearchIcon,
  StorageOutlined as ConnectionIcon,
  SchemaOutlined as SchemaIcon,
  TableChartOutlined as TableIcon,
  LightbulbOutlined as DataAssetsIcon,
} from "@mui/icons-material";
import { useLocation, useNavigate } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import { pageShellSx, panelSx } from "~/theme";
import {
  fetchExploreData,
} from "~/stores/slices/exploreSlice/index";
import TableDetail from "./Tables/TableDetail/TableDetail";

const normalizeTable = (table, connection = null) => {
  if (typeof table === "string") {
    const [schemaName, ...rest] = table.split(".");
    const assetName = rest.join(".") || table;
    return {
      full_name: table,
      table_name: assetName,
      schema_name: rest.length ? schemaName : "",
      connectionName: connection?.name,
      connectionOwner: connection?.owner,
      connectionId: connection?.id,
    };
  }

  const conn = table.connection || connection;
  return {
    full_name: table.full_name || table.table_name || "",
    table_name: table.table_name || "",
    schema_name: table.schema_name || "",
    connectionName: conn?.name,
    connectionOwner: conn?.owner,
    connectionId: conn?.id,
  };
};

const getOwnerLabel = (owner) => owner?.full_name || owner?.username || owner?.email || "System";

const Explore = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const location = useLocation();
  const searchParams = useMemo(() => new URLSearchParams(location.search), [location.search]);
  
  let tableParam = searchParams.get("table");
  let schemaParam = searchParams.get("schema");
  const connectionParam = searchParams.get("connection") || searchParams.get("service");
  const sectionParam = searchParams.get("section") || "overview";
  const observabilityTabParam = searchParams.get("obsTab") || "metadata";

  if (tableParam && tableParam.includes(".")) {
    const parts = tableParam.split(".");
    if (!schemaParam) schemaParam = parts[0];
    tableParam = parts.slice(1).join(".");
  }

  const connections = useSelector((state) => state.explore.discovery.connections) || [];
  const connectionsStatus = useSelector((state) => state.explore.discovery.connectionsStatus);
  const connectionsError = useSelector((state) => state.explore.discovery.connectionsError);
  const exploreDataLoaded = useSelector((state) => state.explore.discovery.exploreDataLoaded);
  const schemasMap = useSelector((state) => state.explore.discovery.schemasByConnection) || {};
  const tablesMap = useSelector((state) => state.explore.discovery.tablesByConnection) || {};

  const [selectedConnectionId, setSelectedConnectionId] = useState(null);
  const [selectedSchemaByConnection, setSelectedSchemaByConnection] = useState({});
  const [searchQuery, setSearchQuery] = useState("");
  const [isDatabasesExpanded, setIsDatabasesExpanded] = useState(true);
  const [expandedConnections, setExpandedConnections] = useState({});

  useEffect(() => {
    if (!exploreDataLoaded && connectionsStatus !== "loading") {
      dispatch(fetchExploreData());
    }
  }, [dispatch, exploreDataLoaded, connectionsStatus]);

  const loading = connectionsStatus === "loading" && !exploreDataLoaded;
  const error = connectionsStatus === "failed" ? connectionsError : null;

  const resolvedSelectedConnectionId =
    selectedConnectionId && connections.some((c) => c.id === selectedConnectionId)
      ? selectedConnectionId
      : null;

  const selectedConnection =
    connections.find((c) => c.id === resolvedSelectedConnectionId) || null;

  const selectedSchema = resolvedSelectedConnectionId
    ? selectedSchemaByConnection[resolvedSelectedConnectionId] || "all"
    : "all";

  const allNormalizedTables = useMemo(() => {
    if (!resolvedSelectedConnectionId) {
      return Object.entries(tablesMap).flatMap(([connId, tables]) => {
        const conn = connections.find(c => String(c.id) === connId);
        return (tables || []).map(t => normalizeTable(t, conn));
      });
    }
    const conn = connections.find(c => c.id === resolvedSelectedConnectionId);
    return (tablesMap[resolvedSelectedConnectionId] || []).map(t => normalizeTable(t, conn));
  }, [resolvedSelectedConnectionId, tablesMap, connections]);

  const visibleTables = allNormalizedTables.filter((table) => {
    const matchesSchema = selectedSchema === "all" || table.schema_name === selectedSchema;
    if (!matchesSchema) return false;
    if (!searchQuery.trim()) return true;

    const normQuery = searchQuery.trim().toLowerCase();
    const haystack = [table.table_name, table.schema_name, table.full_name].filter(Boolean).join(" ").toLowerCase();
    return haystack.includes(normQuery);
  });

  const updateExploreQuery = useCallback(
    ({ connectionId = connectionParam, schemaName = schemaParam, tableName = tableParam, section = sectionParam, obsTab = observabilityTabParam } = {}) => {
      const params = new URLSearchParams();
      if (connectionId) params.set("connection", connectionId);
      if (schemaName) params.set("schema", schemaName);
      if (tableName) {
        // Ensure we only store the table name part if it's qualified
        const cleanTable = tableName.includes('.') ? tableName.split('.').pop() : tableName;
        params.set("table", cleanTable);
      }
      if (section && section !== "overview") params.set("section", section);
      if (obsTab && obsTab !== "metadata") params.set("obsTab", obsTab);
      navigate(`/explore${params.toString() ? `?${params.toString()}` : ""}`);
    },
    [navigate, observabilityTabParam, sectionParam, connectionParam, schemaParam, tableParam]
  );

  const openAssetDetail = (connectionId, schemaName, tableName) => {
    updateExploreQuery({ connectionId, schemaName, tableName, section: "overview", obsTab: "metadata" });
  };

  if (loading) {
    return <Box sx={{ display: "flex", justifyContent: "center", py: 10 }}><CircularProgress size={32} /></Box>;
  }

  if (tableParam && connectionParam) {
    return (
      <TableDetail
        tableName={tableParam}
        schemaName={schemaParam}
        connectionId={Number(connectionParam)}
        onBack={() => navigate("/explore")}
        onChangeSection={(nextSection, nextObsTab = observabilityTabParam) =>
          updateExploreQuery({ connectionId: connectionParam, schemaName: schemaParam, tableName: tableParam, section: nextSection, obsTab: nextObsTab })
        }
        observabilityTab={observabilityTabParam}
        section={sectionParam}
      />
    );
  }

  return (
    <Box sx={pageShellSx}>
      <Stack direction={{ xs: "column", lg: "row" }} spacing={2.5} alignItems="stretch">
        {/* Left Sidebar */}
        <Paper sx={{ width: { xs: "100%", lg: 300 }, minWidth: { lg: 300 }, p: 2, ...panelSx, borderRadius: 3 }}>
          <Stack spacing={2} sx={{ height: "100%" }}>
            <Stack direction="row" alignItems="center" spacing={1} sx={{ cursor: "pointer" }} onClick={() => { setSelectedConnectionId(null); setSearchQuery(""); }}>
              <DataAssetsIcon sx={{ fontSize: 20, color: "primary.main" }} />
              <Typography sx={{ fontSize: 16, fontWeight: 900 }}>Data Infrastructure</Typography>
            </Stack>

            <TextField
              size="small"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search tables..."
              InputProps={{
                startAdornment: <InputAdornment position="start"><SearchIcon fontSize="small" /></InputAdornment>,
                sx: { borderRadius: 2, bgcolor: '#f8fafc' }
              }}
            />

            <Box sx={{ overflow: "auto", flexGrow: 1 }}>
              <List disablePadding>
                <ListItemButton onClick={() => setIsDatabasesExpanded(!isDatabasesExpanded)} sx={{ borderRadius: 2 }}>
                  {isDatabasesExpanded ? <ExpandMoreIcon /> : <ChevronRightIcon />}
                  <ConnectionIcon sx={{ ml: 1, mr: 1 }} />
                  <ListItemText primary="Connections" slotProps={{ primary: { fontWeight: 800, fontSize: 14 } }} />
                </ListItemButton>

                {isDatabasesExpanded && connections.map((conn) => {
                  const isExpanded = expandedConnections[conn.id] ?? (conn.id === resolvedSelectedConnectionId);
                  const schemas = schemasMap[conn.id] || [];
                  
                  return (
                    <Box key={conn.id} sx={{ ml: 2 }}>
                      <ListItemButton onClick={() => setExpandedConnections({ ...expandedConnections, [conn.id]: !isExpanded })} sx={{ borderRadius: 2 }}>
                        {schemas.length > 0 ? (isExpanded ? <ExpandMoreIcon fontSize="small" /> : <ChevronRightIcon fontSize="small" />) : <Box sx={{ width: 20 }} />}
                        <ConnectionIcon sx={{ fontSize: 16, mx: 1 }} />
                        <ListItemText primary={conn.name} slotProps={{ primary: { fontWeight: 600, fontSize: 13 } }} />
                      </ListItemButton>

                      {isExpanded && schemas.map((schema) => (
                        <ListItemButton 
                          key={schema} 
                          selected={selectedConnectionId === conn.id && selectedSchema === schema}
                          onClick={() => {
                            setSelectedConnectionId(conn.id);
                            setSelectedSchemaByConnection({ ...selectedSchemaByConnection, [conn.id]: schema });
                          }}
                          sx={{ ml: 3, borderRadius: 2, my: 0.25 }}
                        >
                          <SchemaIcon sx={{ fontSize: 14, mr: 1, color: 'text.secondary' }} />
                          <ListItemText primary={schema} slotProps={{ primary: { fontSize: 12, fontWeight: (selectedSchema === schema) ? 800 : 400 } }} />
                        </ListItemButton>
                      ))}
                    </Box>
                  );
                })}
              </List>
            </Box>
          </Stack>
        </Paper>

        {/* Right Content */}
        <Box sx={{ flex: 1, minWidth: 0 }}>
          {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}

          <Paper sx={{ p: 3, ...panelSx, borderRadius: 3 }}>
            <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 2 }}>
              <Box>
                <Typography variant="h5" fontWeight="900">{selectedConnection?.name || "All Data Assets"}</Typography>
                <Typography variant="body2" color="text.secondary">
                  {selectedSchema === "all" ? `${visibleTables.length} tables integrated` : `Viewing ${visibleTables.length} tables in ${selectedSchema}`}
                </Typography>
              </Box>
              <Button size="small" startIcon={<RefreshIcon />} onClick={() => dispatch(fetchExploreData())} variant="outlined" sx={{ borderRadius: 2 }}>Refresh</Button>
            </Stack>
            <Divider sx={{ mb: 3 }} />

            <Stack spacing={2}>
              {visibleTables.map((table) => (
                <Paper
                  key={table.full_name}
                  onClick={() => openAssetDetail(table.connectionId || resolvedSelectedConnectionId, table.schema_name, table.table_name)}
                  sx={{
                    p: 2.5, borderRadius: 3, border: '1px solid #f1f5f9', cursor: 'pointer',
                    '&:hover': { bgcolor: '#f8fafc', transform: 'translateX(4px)', transition: 'all 0.2s' }
                  }}
                >
                  <Stack direction="row" spacing={2} alignItems="center">
                    <Avatar sx={{ bgcolor: 'primary.50', color: 'primary.main' }}><TableIcon /></Avatar>
                    <Box sx={{ flex: 1 }}>
                      <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600 }}>{table.connectionName} / {table.schema_name}</Typography>
                      <Typography variant="h6" fontWeight="900" color="primary.dark">{table.table_name}</Typography>
                      <Stack direction="row" spacing={1} sx={{ mt: 1 }}>
                        <Chip icon={<OwnerIcon sx={{ fontSize: '14px !important' }} />} label={getOwnerLabel(table.connectionOwner)} size="small" variant="outlined" />
                      </Stack>
                    </Box>
                    <ChevronRightIcon color="disabled" />
                  </Stack>
                </Paper>
              ))}
              {visibleTables.length === 0 && (
                <Box sx={{ py: 10, textAlign: 'center' }}>
                  <Typography color="text.secondary">No tables found. Adjust filters or contact Admin for access.</Typography>
                </Box>
              )}
            </Stack>
          </Paper>
        </Box>
      </Stack>
    </Box>
  );
};

export default Explore;
