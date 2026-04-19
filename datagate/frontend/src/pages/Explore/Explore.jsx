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
  StorageOutlined as ServiceIcon,
  SchemaOutlined as SchemaIcon,
  TableChartOutlined as TableIcon,
  LightbulbOutlined as DataAssetsIcon,
  LanOutlined as PipelinesIcon,
  ApiOutlined as ApisIcon,
  GavelOutlined as GovernanceIcon,
  PublicOutlined as DomainsIcon,
} from "@mui/icons-material";
import { useLocation, useNavigate } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import { datagateColors, pageShellSx, panelSx } from "~/theme";
import {
  fetchExploreData,
  fetchServiceSchemas,
  fetchServiceTables,
} from "~/stores/slices/exploreSlice/index";
import TableView from "./Table/Table";

const normalizeTable = (table, service = null) => {
  if (typeof table === "string") {
    const [schemaName, ...rest] = table.split(".");
    const assetName = rest.join(".") || table;
    return {
      full_name: table,
      table_name: assetName,
      schema_name: rest.length ? schemaName : "",
      serviceName: service?.name,
      serviceOwner: service?.owner,
      serviceId: service?.id,
    };
  }

  const svc = table.service || service;
  return {
    full_name: table.full_name || table.table_name || "",
    table_name: table.table_name || "",
    schema_name: table.schema_name || "",
    serviceName: svc?.name,
    serviceOwner: svc?.owner,
    serviceId: svc?.id,
  };
};

const getOwnerLabel = (owner) => owner?.full_name || owner?.username || owner?.email || "Unknown owner";

const Explore = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const location = useLocation();
  const searchParams = useMemo(() => new URLSearchParams(location.search), [location.search]);
  let tableParam = searchParams.get("table");
  let schemaParam = searchParams.get("schema");
  const serviceParam = searchParams.get("service");
  const sectionParam = searchParams.get("section") || "overview";
  const observabilityTabParam = searchParams.get("obsTab") || "metadata";

  // Backward compatibility: If old URL had ?table=schema.table
  if (!schemaParam && tableParam && tableParam.includes(".")) {
    const parts = tableParam.split(".");
    schemaParam = parts[0];
    tableParam = parts.slice(1).join(".");
  }
  const services = useSelector((state) => state.explore.discovery.services);
  const servicesStatus = useSelector((state) => state.explore.discovery.servicesStatus);
  const servicesError = useSelector((state) => state.explore.discovery.servicesError);
  const exploreDataLoaded = useSelector((state) => state.explore.discovery.exploreDataLoaded);
  const schemasMap = useSelector((state) => state.explore.discovery.schemasByService);
  const tablesMap = useSelector((state) => state.explore.discovery.tablesByService);
  const loadingTablesByService = useSelector((state) => state.explore.discovery.tablesStatusByService);

  const [selectedServiceId, setSelectedServiceId] = useState(null);
  const [selectedSchemaByService, setSelectedSchemaByService] = useState({});
  const [searchQuery, setSearchQuery] = useState("");
  const [isDatabasesExpanded, setIsDatabasesExpanded] = useState(true);
  const [expandedServiceTypes, setExpandedServiceTypes] = useState({});
  const [expandedServices, setExpandedServices] = useState({});

  useEffect(() => {
    if (!exploreDataLoaded && servicesStatus !== "loading") {
      dispatch(fetchExploreData());
    }
  }, [dispatch, exploreDataLoaded, servicesStatus]);

  const loading = servicesStatus === "loading";
  const error =
    servicesStatus === "failed"
      ? servicesError || "Could not load data platform services. Please check connection."
      : null;
  const resolvedSelectedServiceId =
    selectedServiceId && services.some((service) => service.id === selectedServiceId)
      ? selectedServiceId
      : null;
  const selectedService =
    services.find((service) => service.id === resolvedSelectedServiceId) || null;
  const selectedSchema = resolvedSelectedServiceId
    ? selectedSchemaByService[resolvedSelectedServiceId] || "all"
    : "all";

  const allNormalizedTables = useMemo(() => {
    if (!resolvedSelectedServiceId) {
      return Object.entries(tablesMap).flatMap(([svcId, tables]) => {
        const svc = services.find(s => String(s.id) === svcId);
        return (tables || []).map(t => normalizeTable(t, svc));
      });
    }
    const svc = services.find(s => s.id === resolvedSelectedServiceId);
    return (tablesMap[resolvedSelectedServiceId] || []).map(t => normalizeTable(t, svc));
  }, [resolvedSelectedServiceId, tablesMap, services]);

  const selectedServiceTables = allNormalizedTables;
  const normalizedSearchQuery = searchQuery.trim().toLowerCase();

  const updateExploreQuery = useCallback(
    ({ serviceId = serviceParam, schemaName = schemaParam, tableName = tableParam, section = sectionParam, obsTab = observabilityTabParam } = {}) => {
      const params = new URLSearchParams();
      if (serviceId) params.set("service", serviceId);
      if (schemaName) params.set("schema", schemaName);
      if (tableName) params.set("table", tableName);
      if (section && section !== "overview") params.set("section", section);
      if (obsTab && obsTab !== "metadata") params.set("obsTab", obsTab);
      navigate(`/explore${params.toString() ? `?${params.toString()}` : ""}`);
    },
    [navigate, observabilityTabParam, sectionParam, serviceParam, schemaParam, tableParam]
  );

  const handleBackToExplore = () => {
    navigate("/explore");
  };

  const groupedServices = services.reduce((accumulator, service) => {
    const key = (service.service_type || "Other").toLowerCase();
    if (!accumulator[key]) {
      accumulator[key] = {
        label: service.service_type || "Other",
        services: [],
      };
    }
    accumulator[key].services.push(service);
    return accumulator;
  }, {});

  const visibleTables = selectedServiceTables.filter((table) => {
    const matchesSchema = selectedSchema === "all" || table.schema_name === selectedSchema;
    if (!matchesSchema) return false;
    if (!normalizedSearchQuery) return true;

    const haystack = [table.table_name, table.schema_name, table.full_name]
      .filter(Boolean)
      .join(" ")
      .toLowerCase();

    return haystack.includes(normalizedSearchQuery);
  });

  // Asset Detail logic removed, moved to TableView component
  
  const assetCards = visibleTables.map((table, index) => ({
    ...table,
    summary: `${table.serviceName || selectedService?.name || "data_asset"} / ${table.schema_name || "default"} / ${table.table_name}`,
    description: table.full_name || table.table_name,
    ownerLabel: getOwnerLabel(table.serviceOwner || selectedService?.owner),
    accent: index === 0 ? "#F7FAFF" : "#FFFFFF",
    border: index === 0 ? "#7BA7FF" : "#EEF2F7",
  }));

  const openAssetDetail = (serviceId, schemaName, tableName) => {
    updateExploreQuery({ serviceId, schemaName, tableName, section: "overview", obsTab: "metadata" });
  };

  if (loading) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", py: 10 }}>
        <CircularProgress size={32} />
      </Box>
    );
  }

  if (tableParam && serviceParam) {
    return (
      <TableView
        tableName={tableParam}
        schemaName={schemaParam}
        serviceId={Number(serviceParam)}
        onBack={handleBackToExplore}
        onChangeSection={(nextSection, nextObsTab = observabilityTabParam) =>
          updateExploreQuery({
            serviceId: serviceParam,
            schemaName: schemaParam,
            tableName: tableParam,
            section: nextSection,
            obsTab: nextObsTab,
          })
        }
        observabilityTab={observabilityTabParam}
        section={sectionParam}
      />
    );
  }

  return (
    <Box sx={pageShellSx}>
      <Stack direction={{ xs: "column", lg: "row" }} spacing={2.5} alignItems="stretch">
        <Paper
          sx={{
            width: { xs: "100%", lg: 300 },
            minWidth: { lg: 300 },
            p: 1.75,
            ...panelSx,
            borderRadius: 1,
          }}
        >
          <Stack spacing={1.5} sx={{ height: "100%" }}>
            <Stack
              direction="row"
              alignItems="center"
              spacing={1}
              sx={{ px: 0.5, cursor: "pointer", "&:hover": { opacity: 0.7 } }}
              onClick={() => {
                setSelectedServiceId(null);
                setSearchQuery("");
              }}
            >
              <DataAssetsIcon sx={{ fontSize: 20, color: "#4B91F7" }} />
              <Typography sx={{ fontSize: 16, fontWeight: 700, color: "#1A1A1A" }}>
                Services
              </Typography>
            </Stack>

            <TextField
              size="small"
              value={searchQuery}
              onChange={(event) => setSearchQuery(event.target.value)}
              placeholder="Search assets..."
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon fontSize="small" sx={{ color: "text.disabled" }} />
                  </InputAdornment>
                ),
                sx: {
                  fontSize: 13,
                  bgcolor: "#f8f9fa",
                  "& fieldset": { border: "none" },
                  borderRadius: 1,
                },
              }}
            />
            <Box sx={{ overflow: "auto", pr: 0.5, flexGrow: 1 }}>
              <List disablePadding>
                {/* Services Header */}
                <ListItemButton
                  onClick={() => setIsDatabasesExpanded((prev) => !prev)}
                  sx={{ px: 0.5, py: 0.75, borderRadius: 1, mb: 0.25, minHeight: 32 }}
                >
                  {isDatabasesExpanded ? (
                    <ExpandMoreIcon sx={{ fontSize: 18, color: "text.secondary" }} />
                  ) : (
                    <ChevronRightIcon sx={{ fontSize: 18, color: "text.secondary" }} />
                  )}
                  <ServiceIcon sx={{ ml: 0.5, mr: 1, color: "text.secondary", fontSize: 18 }} />
                  <ListItemText
                    primary="Services"
                    slotProps={{ primary: { fontWeight: 600, fontSize: 14, color: "text.primary" } }}
                  />
                </ListItemButton>

                {isDatabasesExpanded &&
                  Object.entries(groupedServices).map(([serviceTypeKey, group]) => {
                    return group.services.map((service) => {
                      const isServiceSelected = service.id === resolvedSelectedServiceId;
                      const isServiceExpanded = expandedServices[service.id] ?? isServiceSelected;
                      const serviceSchemas = schemasMap[service.id] || [];

                      return (
                        <Box key={service.id} sx={{ ml: 2 }}>
                          <ListItemButton
                            onClick={() => {
                              setExpandedServices((prev) => ({
                                ...prev,
                                [service.id]: !isServiceExpanded,
                              }));
                            }}
                            sx={{
                              borderRadius: 1,
                              py: 0.5,
                              mb: 0.25,
                              minHeight: 32,
                            }}
                          >
                            <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                              {serviceSchemas.length > 0 ? (
                                isServiceExpanded ? (
                                  <ExpandMoreIcon sx={{ fontSize: 16, color: "text.secondary", mr: 0.5 }} />
                                ) : (
                                  <ChevronRightIcon sx={{ fontSize: 16, color: "text.secondary", mr: 0.5 }} />
                                )
                              ) : (
                                <Box sx={{ width: 21 }} />
                              )}
                              
                              <ServiceIcon sx={{ fontSize: 16, color: "text.secondary", mr: 1 }} />

                              <ListItemText
                                primary={service.name}
                                slotProps={{
                                  primary: { fontWeight: 500, fontSize: 13.5 },
                                }}
                              />
                            </Box>
                          </ListItemButton>

                          {isServiceExpanded && (
                            <Box sx={{ ml: 2, borderLeft: "1px solid #eee" }}>
                              {serviceSchemas.map((schema) => {
                                const isSchemaSelected = isServiceSelected && selectedSchema === schema;
                                
                                return (
                                  <ListItemButton
                                    key={schema}
                                    selected={isSchemaSelected}
                                    onClick={() => {
                                      setSelectedServiceId(service.id);
                                      setSelectedSchemaByService((prev) => ({
                                        ...prev,
                                        [service.id]: schema,
                                      }));
                                    }}
                                    sx={{
                                      ml: 1,
                                      borderRadius: 1,
                                      py: 0.25,
                                      minHeight: 28,
                                      bgcolor: isSchemaSelected ? "rgba(75, 145, 247, 0.08)" : "transparent",
                                      "&.Mui-selected": {
                                        bgcolor: "rgba(75, 145, 247, 0.12)",
                                        "&:hover": { bgcolor: "rgba(75, 145, 247, 0.16)" },
                                      },
                                    }}
                                  >
                                    <SchemaIcon sx={{ mr: 1, color: "text.secondary", fontSize: 14 }} />
                                    <ListItemText
                                      primary={schema}
                                      slotProps={{
                                        primary: { fontSize: 12.5, fontWeight: isSchemaSelected ? 600 : 400 },
                                      }}
                                    />
                                  </ListItemButton>
                                );
                              })}
                            </Box>
                          )}
                        </Box>
                      );
                    });
                  })}

              </List>
            </Box>
          </Stack>
        </Paper>

        <Box sx={{ flex: 1, minWidth: 0 }}>
          {error ? <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert> : null}

          <Paper
            sx={{
              p: 2,
              ...panelSx,
            }}
          >
            <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 1.5 }}>
              <Box>
                <Typography sx={{ fontSize: 18, fontWeight: 700 }}>
                  {selectedService?.name || "Tables"}
                </Typography>
                <Typography sx={{ fontSize: 12.5 }} color="text.secondary">
                  {selectedSchema === "all"
                    ? `${visibleTables.length} tables available`
                    : `${visibleTables.length} tables in schema ${selectedSchema}`}
                </Typography>
              </Box>
              <Stack direction="row" spacing={1}>
                <Button size="small" variant="outlined" startIcon={<RefreshIcon />} onClick={() => dispatch(fetchExploreData())} sx={{ textTransform: "none", fontSize: 12, borderColor: "#E6EBF2" }}>
                  Refresh
                </Button>
              </Stack>
            </Stack>

            <Divider sx={{ mb: 2 }} />

            {loadingTablesByService[resolvedSelectedServiceId] === "loading" ? (
              <Box sx={{ display: "flex", justifyContent: "center", py: 10 }}>
                <CircularProgress size={28} />
              </Box>
            ) : assetCards.length === 0 ? (
              <Box sx={{ py: 10, textAlign: "center" }}>
                <Typography variant="h6" sx={{ mb: 1 }}>
                  Không có asset phù hợp
                </Typography>
                <Typography color="text.secondary">
                  Thử chọn service khác hoặc đổi từ khóa tìm kiếm.
                </Typography>
              </Box>
            ) : (
              <Stack spacing={2.5}>
                {assetCards.map((table) => (
                  <Paper
                    key={`${table.serviceId}_${table.schema_name}_${table.table_name}`}
                    onClick={() => openAssetDetail(table.serviceId || resolvedSelectedServiceId, table.schema_name, table.table_name)}
                    sx={{
                      p: 2,
                      borderRadius: 1,
                      border: `1px solid ${table.border}`,
                      borderLeft: `3px solid ${table.border}`,
                      bgcolor: table.accent,
                      cursor: "pointer",
                      transition: "transform 0.2s ease, box-shadow 0.2s ease",
                      "&:hover": {
                        transform: "translateY(-2px)",
                        boxShadow: "0 8px 18px rgba(15, 23, 42, 0.06)",
                      },
                    }}
                  >
                    <Stack direction={{ xs: "column", md: "row" }} spacing={1.5} alignItems={{ md: "flex-start" }}>
                      <Avatar sx={{ bgcolor: "#EEF4FF", color: "primary.main", width: 38, height: 38 }}>
                        <TableIcon sx={{ fontSize: 18 }} />
                      </Avatar>

                      <Box sx={{ flex: 1, minWidth: 0 }}>
                        <Typography
                          color="text.secondary"
                          sx={{ mb: 0.5, wordBreak: "break-word", fontSize: 12.5 }}
                        >
                          {table.summary}
                        </Typography>

                        <Typography
                          sx={{ color: "#2F6FED", fontWeight: 700, mb: 0.75, textTransform: "lowercase", fontSize: 24 }}
                        >
                          {table.table_name}
                        </Typography>

                        <Typography color="text.secondary" sx={{ mb: 1.5, fontSize: 13.5 }}>
                          {table.description}
                        </Typography>

                        <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap alignItems="center">
                          <Chip
                            icon={<OwnerIcon />}
                            label={table.ownerLabel}
                            size="small"
                            variant="outlined"
                            sx={{ height: 24, fontSize: 11.5, borderColor: "#E6EBF2" }}
                          />
                        </Stack>
                      </Box>
                    </Stack>
                  </Paper>
                ))}
              </Stack>
            )}
          </Paper>
        </Box>
      </Stack>
    </Box>
  );
};

export default Explore;
