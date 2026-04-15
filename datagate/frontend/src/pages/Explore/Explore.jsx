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
} from "@mui/icons-material";
import { useLocation, useNavigate } from "react-router-dom";
import { observabilityApi } from "~/apis/observability";
import { servicesApi } from "~/apis/services";
import TableView from "./Table/Table";

const normalizeTable = (table) => {
  if (typeof table === "string") {
    const [schemaName, ...rest] = table.split(".");
    const assetName = rest.join(".") || table;
    return {
      full_name: table,
      table_name: assetName,
      schema_name: rest.length ? schemaName : "",
    };
  }

  return {
    full_name: table.full_name || table.table_name || "",
    table_name: table.table_name || "",
    schema_name: table.schema_name || "",
  };
};

const getOwnerLabel = (owner) => owner?.full_name || owner?.username || owner?.email || "Unknown owner";

const Explore = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const searchParams = useMemo(() => new URLSearchParams(location.search), [location.search]);
  const tableParam = searchParams.get("table");
  const serviceParam = searchParams.get("service");

  const [selectedServiceId, setSelectedServiceId] = useState(null);
  const [selectedSchemaByService, setSelectedSchemaByService] = useState({});
  const [services, setServices] = useState([]);
  const [schemasMap, setSchemasMap] = useState({});
  const [tablesMap, setTablesMap] = useState({});
  const [loading, setLoading] = useState(true);
  const [, setLoadingSchemas] = useState({});
  const [loadingTables, setLoadingTables] = useState({});
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [isDatabasesExpanded, setIsDatabasesExpanded] = useState(true);
  const [expandedServiceTypes, setExpandedServiceTypes] = useState({});
  const [expandedServices, setExpandedServices] = useState({});

  const [sampleLimit, setSampleLimit] = useState(50);
  const [assetDetail, setAssetDetail] = useState(null);
  const [assetDetailLoading, setAssetDetailLoading] = useState(false);
  const [assetDetailError, setAssetDetailError] = useState(null);
  const [assetObservability, setAssetObservability] = useState({
    columnStats: [],
    incidents: [],
    schema: [],
    snapshots: [],
    volume: [],
  });

  const fetchServices = useCallback(async () => {
    try {
      setLoading(true);
      const response = await servicesApi.getServices();
      const nextServices = response.data || [];
      setServices(nextServices);
      setSelectedServiceId((prev) =>
        prev && nextServices.some((service) => service.id === prev) ? prev : nextServices[0]?.id ?? null
      );
      setError(null);
    } catch (err) {
      console.error("Failed to fetch services:", err);
      setError("Could not load data platform services. Please check connection.");
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchSchemas = useCallback(async (serviceId) => {
    if (!serviceId || schemasMap[serviceId]) return;

    try {
      setLoadingSchemas((prev) => ({ ...prev, [serviceId]: true }));
      const response = await servicesApi.getServiceSchemas(serviceId);
      const schemas = response.data || [];
      setSchemasMap((prev) => ({ ...prev, [serviceId]: schemas }));
      setSelectedSchemaByService((prev) => ({
        ...prev,
        [serviceId]: prev[serviceId] || schemas[0] || "all",
      }));
    } catch (err) {
      console.error(`Failed to fetch schemas for ${serviceId}:`, err);
    } finally {
      setLoadingSchemas((prev) => ({ ...prev, [serviceId]: false }));
    }
  }, [schemasMap]);

  const fetchTables = useCallback(async (serviceId) => {
    if (!serviceId || tablesMap[serviceId]) return;

    try {
      setLoadingTables((prev) => ({ ...prev, [serviceId]: true }));
      const response = await servicesApi.getServiceTables(serviceId);
      setTablesMap((prev) => ({
        ...prev,
        [serviceId]: (response.data || []).map(normalizeTable),
      }));
    } catch (err) {
      console.error(`Failed to fetch tables for ${serviceId}:`, err);
    } finally {
      setLoadingTables((prev) => ({ ...prev, [serviceId]: false }));
    }
  }, [tablesMap]);

  useEffect(() => {
    fetchServices();
  }, [fetchServices]);

  useEffect(() => {
    if (!selectedServiceId || tableParam) return;
    fetchSchemas(selectedServiceId);
    fetchTables(selectedServiceId);
  }, [fetchSchemas, fetchTables, selectedServiceId, tableParam]);

  useEffect(() => {
    if (!selectedServiceId) return;

    const nextService = services.find((service) => service.id === selectedServiceId);
    if (!nextService) return;

    const nextServiceType = (nextService.service_type || "Other").toLowerCase();
    setExpandedServiceTypes((prev) => ({ ...prev, [nextServiceType]: true }));
    setExpandedServices((prev) => ({ ...prev, [selectedServiceId]: true }));
  }, [selectedServiceId, services]);

  useEffect(() => {
    if (!tableParam || !serviceParam) {
      setAssetDetail(null);
      setAssetDetailError(null);
      return;
    }

    const fetchAssetDetail = async () => {
      try {
        setAssetDetailLoading(true);
        setAssetDetailError(null);
        const [detailRes, snapshotsRes, schemaRes, columnStatsRes, incidentsRes, volumeRes] = await Promise.all([
          servicesApi.getAssetDetail(tableParam, Number(serviceParam), sampleLimit),
          observabilityApi.getSnapshots(tableParam),
          observabilityApi.getSchema(tableParam),
          observabilityApi.getColumnStats(tableParam),
          observabilityApi.getIncidents(tableParam),
          observabilityApi.getVolumeTS(tableParam),
        ]);

        setAssetDetail(detailRes.data);
        setAssetObservability({
          columnStats: columnStatsRes.data || [],
          incidents: incidentsRes.data || [],
          schema: schemaRes.data || [],
          snapshots: snapshotsRes.data || [],
          volume: volumeRes.data || [],
        });
      } catch (err) {
        console.error("Failed to fetch asset detail:", err);
        setAssetDetailError("Could not load asset details.");
      } finally {
        setAssetDetailLoading(false);
      }
    };

    fetchAssetDetail();
  }, [tableParam, serviceParam, sampleLimit]);

  const openAssetDetail = (serviceId, tableName) => {
    navigate(`/explore?service=${serviceId}&table=${encodeURIComponent(tableName)}`);
  };

  const closeAssetDetail = () => {
    navigate("/explore");
  };

  const selectedService = services.find((service) => service.id === selectedServiceId) || null;
  const selectedSchema = selectedServiceId ? selectedSchemaByService[selectedServiceId] || "all" : "all";
  const selectedServiceTables = selectedServiceId ? tablesMap[selectedServiceId] || [] : [];
  const normalizedSearchQuery = searchQuery.trim().toLowerCase();
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

  const assetCards = visibleTables.map((table, index) => ({
    ...table,
    summary: `${selectedService?.name || "data_asset"} / ${table.schema_name || "default"} / ${table.table_name}`,
    description: table.full_name || table.table_name,
    ownerLabel: getOwnerLabel(selectedService?.owner),
    accent: index === 0 ? "#F7FAFF" : "#FFFFFF",
    border: index === 0 ? "#7BA7FF" : "#EEF2F7",
  }));

  if (loading) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", py: 10 }}>
        <CircularProgress size={32} />
      </Box>
    );
  }

  if (tableParam && serviceParam) {
    if (assetDetailLoading) {
      return (
        <Box sx={{ display: "flex", justifyContent: "center", py: 10 }}>
          <CircularProgress size={28} />
        </Box>
      );
    }

    if (assetDetailError) {
      return <Alert severity="error">{assetDetailError}</Alert>;
    }

    if (!assetDetail) return null;

    return (
      <TableView
        assetDetail={assetDetail}
        assetObservability={assetObservability}
        onBack={closeAssetDetail}
        onChangeSampleLimit={setSampleLimit}
        sampleLimit={sampleLimit}
      />
    );
  }

  return (
    <Box sx={{ p: 2.5, height: "100%", overflow: "auto", bgcolor: "#F7F9FC" }}>
      <Stack direction={{ xs: "column", lg: "row" }} spacing={2.5} alignItems="stretch">
        <Paper
          sx={{
            width: { xs: "100%", lg: 300 },
            minWidth: { lg: 300 },
            p: 1.75,
            borderRadius: 3,
            border: "1px solid #EEF2F7",
            boxShadow: "0 2px 10px rgba(15, 23, 42, 0.03)",
          }}
        >
          <Stack spacing={1.5} sx={{ height: "100%" }}>
            <Stack direction="row" alignItems="center" justifyContent="space-between">
              <Typography sx={{ fontSize: 18, fontWeight: 800 }}>
                Data Assets
              </Typography>
              <Avatar sx={{ width: 28, height: 28, bgcolor: "#EEF4FF", color: "primary.main" }}>
                <TableIcon sx={{ fontSize: 16 }} />
              </Avatar>
            </Stack>

            <TextField
              size="small"
              value={searchQuery}
              onChange={(event) => setSearchQuery(event.target.value)}
              placeholder="Search table..."
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon fontSize="small" />
                  </InputAdornment>
                ),
                sx: {
                  fontSize: 14,
                  borderRadius: 2,
                },
              }}
            />
            <Box sx={{ overflow: "auto", pr: 0.5 }}>
              <List disablePadding>
                <ListItemButton
                  onClick={() => setIsDatabasesExpanded((prev) => !prev)}
                  sx={{ px: 0.25, py: 0.5, borderRadius: 2, mb: 0.25, minHeight: 32 }}
                >
                  {isDatabasesExpanded ? <ExpandMoreIcon sx={{ fontSize: 18 }} /> : <ChevronRightIcon sx={{ fontSize: 18 }} />}
                  <ServiceIcon sx={{ ml: 0.75, mr: 1, color: "text.secondary", fontSize: 18 }} />
                  <ListItemText
                    primary="Databases"
                    primaryTypographyProps={{ fontWeight: 700, fontSize: 14 }}
                  />
                </ListItemButton>

                {isDatabasesExpanded
                  ? Object.entries(groupedServices).map(([serviceTypeKey, group]) => {
                      const isTypeExpanded = expandedServiceTypes[serviceTypeKey] ?? true;
                      const matchedServices = group.services.filter((service) => {
                        if (!normalizedSearchQuery) return true;

                        const haystack = [service.name, service.service_type]
                          .filter(Boolean)
                          .join(" ")
                          .toLowerCase();

                        return haystack.includes(normalizedSearchQuery);
                      });

                      if (matchedServices.length === 0 && normalizedSearchQuery) {
                        return null;
                      }

                      return (
                        <Box key={serviceTypeKey} sx={{ ml: 1.5 }}>
                          <ListItemButton
                            onClick={() =>
                              setExpandedServiceTypes((prev) => ({
                                ...prev,
                                [serviceTypeKey]: !isTypeExpanded,
                              }))
                            }
                            sx={{ borderRadius: 2, py: 0.4, minHeight: 30 }}
                          >
                            {isTypeExpanded ? <ExpandMoreIcon sx={{ fontSize: 16 }} /> : <ChevronRightIcon sx={{ fontSize: 16 }} />}
                            <ListItemText
                              primary={group.label}
                              primaryTypographyProps={{ fontWeight: 600, textTransform: "lowercase", fontSize: 13 }}
                              sx={{ ml: 1 }}
                            />
                          </ListItemButton>

                          {isTypeExpanded
                            ? matchedServices.map((service) => {
                                const isSelected = service.id === selectedServiceId;
                                const isServiceExpanded = expandedServices[service.id] ?? isSelected;
                                const serviceSchemas = schemasMap[service.id] || [];
                                const visibleSchemas = serviceSchemas.filter((schema) => {
                                  if (!normalizedSearchQuery) return true;
                                  return schema.toLowerCase().includes(normalizedSearchQuery);
                                });

                                return (
                                  <Box key={service.id} sx={{ ml: 1.5 }}>
                                    <ListItemButton
                                      selected={isSelected}
                                      onClick={() => {
                                        setSelectedServiceId(service.id);
                                        fetchSchemas(service.id);
                                        fetchTables(service.id);
                                      }}
                                      sx={{
                                        borderRadius: 2,
                                        py: 0.45,
                                        mb: 0.25,
                                        minHeight: 34,
                                        bgcolor: isSelected ? "#EEF4FF" : "transparent",
                                        "&.Mui-selected": {
                                          bgcolor: "#EEF4FF",
                                        },
                                      }}
                                    >
                                      <IconButton
                                        size="small"
                                        onClick={(event) => {
                                          event.stopPropagation();
                                          setExpandedServices((prev) => ({
                                            ...prev,
                                            [service.id]: !isServiceExpanded,
                                          }));
                                        }}
                                        sx={{ mr: 0.5, p: 0.25 }}
                                      >
                                        {isServiceExpanded ? (
                                          <ExpandMoreIcon sx={{ fontSize: 16 }} />
                                        ) : (
                                          <ChevronRightIcon sx={{ fontSize: 16 }} />
                                        )}
                                      </IconButton>
                                      <ListItemText
                                        primary={service.name}
                                        secondary={service.service_type}
                                        primaryTypographyProps={{ fontWeight: isSelected ? 700 : 500, fontSize: 13 }}
                                        secondaryTypographyProps={{ fontSize: 11 }}
                                      />
                                    </ListItemButton>

                                    {isServiceExpanded && isSelected
                                      ? visibleSchemas.map((schema) => {
                                          const schemaTableCount = selectedServiceTables.filter(
                                            (table) => table.schema_name === schema
                                          ).length;

                                          return (
                                            <ListItemButton
                                              key={schema}
                                              selected={selectedSchema === schema}
                                              onClick={() =>
                                                setSelectedSchemaByService((prev) => ({
                                                  ...prev,
                                                  [service.id]: schema,
                                                }))
                                              }
                                              sx={{ ml: 3, borderRadius: 2, py: 0.25, minHeight: 28 }}
                                            >
                                              <SchemaIcon sx={{ mr: 1, color: "text.secondary", fontSize: 15 }} />
                                              <ListItemText
                                                primary={schema}
                                                secondary={`${schemaTableCount} tables`}
                                                primaryTypographyProps={{ fontSize: 12.5 }}
                                                secondaryTypographyProps={{ fontSize: 10.5 }}
                                              />
                                            </ListItemButton>
                                          );
                                        })
                                      : null}
                                  </Box>
                                );
                              })
                            : null}
                        </Box>
                      );
                    })
                  : null}
              </List>
            </Box>
          </Stack>
        </Paper>

        <Box sx={{ flex: 1, minWidth: 0 }}>
          {error ? <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert> : null}

          <Paper
            sx={{
              p: 2,
              borderRadius: 3,
              border: "1px solid #EEF2F7",
              boxShadow: "0 2px 10px rgba(15, 23, 42, 0.03)",
            }}
          >
            <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 1.5 }}>
              <Box>
                <Typography sx={{ fontSize: 18, fontWeight: 700 }}>
                  {selectedService?.name || "Data Assets"}
                </Typography>
                <Typography sx={{ fontSize: 12.5 }} color="text.secondary">
                  {selectedSchema === "all"
                    ? `${visibleTables.length} assets available`
                    : `${visibleTables.length} assets in schema ${selectedSchema}`}
                </Typography>
              </Box>
              <Stack direction="row" spacing={1}>
                <Button size="small" variant="outlined" startIcon={<RefreshIcon />} onClick={fetchServices} sx={{ textTransform: "none", fontSize: 12, borderColor: "#E6EBF2" }}>
                  Refresh
                </Button>
              </Stack>
            </Stack>

            <Divider sx={{ mb: 2 }} />

            {loadingTables[selectedServiceId] ? (
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
                    key={table.full_name}
                    onClick={() => openAssetDetail(selectedServiceId, table.full_name)}
                    sx={{
                      p: 2,
                      borderRadius: 3,
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
