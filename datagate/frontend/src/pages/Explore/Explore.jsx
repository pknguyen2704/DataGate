import React from "react";
import { useDispatch, useSelector } from "react-redux";
import {
  Alert,
  Box,
  Breadcrumbs,
  Button,
  Chip,
  FormControl,
  InputAdornment,
  InputLabel,
  List,
  ListItemButton,
  ListItemText,
  MenuItem,
  Paper,
  Select,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";
import {
  RefreshOutlined as RefreshIcon,
  SchemaOutlined as SchemaIcon,
  SearchOutlined as SearchIcon,
  StorageOutlined as CatalogIcon,
  TableChartOutlined as TableIcon,
} from "@mui/icons-material";
import { fetchExploreData } from "~/stores/slices/tableSlice";
import { datagateColors, pageShellSx, panelSx } from "~/theme";
import TableDetail from "./Tables/TableDetail/TableDetail";

const ALL_CATALOGS = "__all_catalogs__";
const ALL_SCHEMAS = "__all_schemas__";

function Explore() {
  const dispatch = useDispatch();
  const [query, setQuery] = React.useState("");
  const [selectedTable, setSelectedTable] = React.useState(null);
  const [selectedCatalog, setSelectedCatalog] = React.useState(ALL_CATALOGS);
  const [selectedSchema, setSelectedSchema] = React.useState(ALL_SCHEMAS);
  const [section, setSection] = React.useState("overview");
  const { catalogs, discoveryStatus, discoveryError } = useSelector(
    (state) => state.explore.discovery
  );

  React.useEffect(() => {
    if (discoveryStatus === "idle") {
      dispatch(fetchExploreData());
    }
  }, [discoveryStatus, dispatch]);

  const catalogOptions = React.useMemo(
    () => catalogs.map((catalog) => catalog.catalog_name),
    [catalogs]
  );

  const activeCatalog = React.useMemo(() => {
    if (selectedCatalog === ALL_CATALOGS) return null;
    return catalogs.find((catalog) => catalog.catalog_name === selectedCatalog) || null;
  }, [catalogs, selectedCatalog]);

  const schemaOptions = React.useMemo(() => {
    if (!activeCatalog) {
      return Array.from(
        new Set(
          catalogs.flatMap((catalog) =>
            (catalog.schemas || []).map((schema) => schema.schema_name)
          )
        )
      ).sort();
    }
    return (activeCatalog.schemas || []).map((schema) => schema.schema_name);
  }, [activeCatalog, catalogs]);

  const groupedSchemas = React.useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    return catalogs
      .filter((catalog) => selectedCatalog === ALL_CATALOGS || catalog.catalog_name === selectedCatalog)
      .map((catalog) => ({
        ...catalog,
        schemas: (catalog.schemas || [])
          .filter((schema) => selectedSchema === ALL_SCHEMAS || schema.schema_name === selectedSchema)
          .map((schema) => ({
            ...schema,
            tables: (schema.tables || []).filter((table) => {
              if (!normalizedQuery) return true;
              return [
                table.full_name,
                table.table_name,
                table.schema_name,
                table.catalog_name,
                table.connection_name,
              ]
                .filter(Boolean)
                .join(" ")
                .toLowerCase()
                .includes(normalizedQuery);
            }),
          }))
          .filter((schema) => schema.tables.length > 0),
      }))
      .filter((catalog) => catalog.schemas.length > 0);
  }, [catalogs, query, selectedCatalog, selectedSchema]);

  const visibleTables = React.useMemo(
    () => groupedSchemas.flatMap((catalog) =>
      catalog.schemas.flatMap((schema) => schema.tables)
    ),
    [groupedSchemas]
  );

  const handleCatalogChange = (catalogName) => {
    setSelectedCatalog(catalogName);
    setSelectedSchema(ALL_SCHEMAS);
  };

  if (selectedTable) {
    return (
      <TableDetail
        tableId={selectedTable.id}
        tableName={selectedTable.table_name}
        schemaName={selectedTable.schema_name}
        catalogName={selectedTable.catalog_name}
        section={section}
        onBack={() => {
          setSelectedTable(null);
          setSection("overview");
        }}
        onChangeSection={setSection}
        onNavigateCrumb={({ catalogName, schemaName }) => {
          setSelectedCatalog(catalogName || ALL_CATALOGS);
          setSelectedSchema(schemaName || ALL_SCHEMAS);
          setSelectedTable(null);
          setSection("overview");
        }}
      />
    );
  }

  return (
    <Box sx={pageShellSx}>
      <Stack spacing={3}>
        <Stack
          direction={{ xs: "column", xl: "row" }}
          spacing={2}
          justifyContent="space-between"
          alignItems={{ xs: "stretch", xl: "center" }}
        >
          <Box>
            <Typography variant="overline" color="primary.main">
              Lakehouse Explorer
            </Typography>
            <Typography variant="h4" fontWeight={800}>
              Explore
            </Typography>
            <Typography color="text.secondary">
              Browse managed assets by catalog and schema, then open metadata, samples, and rules.
            </Typography>
          </Box>
          <Stack direction={{ xs: "column", sm: "row" }} spacing={1.5}>
            <Chip
              icon={<CatalogIcon />}
              label={`${catalogs.length} catalogs`}
              variant="outlined"
              sx={{ bgcolor: "background.paper" }}
            />
            <Chip
              icon={<TableIcon />}
              label={`${visibleTables.length} tables`}
              variant="outlined"
              sx={{ bgcolor: "background.paper" }}
            />
            <Button
              variant="contained"
              startIcon={<RefreshIcon />}
              onClick={() => dispatch(fetchExploreData())}
            >
              Refresh
            </Button>
          </Stack>
        </Stack>

        <Paper sx={{ ...panelSx, p: 2.5 }}>
          <Stack spacing={2}>
            <Breadcrumbs>
              <Typography
                color={selectedCatalog === ALL_CATALOGS ? "text.primary" : "text.secondary"}
                sx={{ fontWeight: 700 }}
              >
                My lakehouse
              </Typography>
              <Typography
                color={selectedCatalog === ALL_CATALOGS ? "text.secondary" : "text.primary"}
                sx={{ fontWeight: 700 }}
              >
                {selectedCatalog === ALL_CATALOGS ? "All catalogs" : selectedCatalog}
              </Typography>
              <Typography color="text.secondary">
                {selectedSchema === ALL_SCHEMAS ? "All schemas" : selectedSchema}
              </Typography>
            </Breadcrumbs>

            <Stack direction={{ xs: "column", lg: "row" }} spacing={2}>
              <TextField
                fullWidth
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Search catalog, schema, table, or source"
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon fontSize="small" />
                    </InputAdornment>
                  ),
                }}
              />
              <FormControl sx={{ minWidth: { xs: "100%", lg: 220 } }}>
                <InputLabel id="catalog-filter-label">Catalog</InputLabel>
                <Select
                  labelId="catalog-filter-label"
                  value={selectedCatalog}
                  label="Catalog"
                  onChange={(event) => handleCatalogChange(event.target.value)}
                >
                  <MenuItem value={ALL_CATALOGS}>All catalogs</MenuItem>
                  {catalogOptions.map((catalogName) => (
                    <MenuItem key={catalogName} value={catalogName}>
                      {catalogName}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              <FormControl sx={{ minWidth: { xs: "100%", lg: 220 } }}>
                <InputLabel id="schema-filter-label">Schema</InputLabel>
                <Select
                  labelId="schema-filter-label"
                  value={selectedSchema}
                  label="Schema"
                  onChange={(event) => setSelectedSchema(event.target.value)}
                >
                  <MenuItem value={ALL_SCHEMAS}>All schemas</MenuItem>
                  {schemaOptions.map((schemaName) => (
                    <MenuItem key={schemaName} value={schemaName}>
                      {schemaName}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Stack>
          </Stack>
        </Paper>

        {discoveryStatus === "failed" ? (
          <Alert severity="error">{discoveryError}</Alert>
        ) : null}

        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: { xs: "1fr", lg: "280px minmax(0, 1fr)" },
            gap: 3,
            alignItems: "start",
          }}
        >
          <Paper sx={{ ...panelSx, p: 1.5, position: { lg: "sticky" }, top: 16 }}>
            <Stack spacing={1.5}>
              <Stack direction="row" spacing={1} alignItems="center" sx={{ px: 1 }}>
                <CatalogIcon color="primary" />
                <Typography variant="subtitle1" fontWeight={800}>
                  Catalogs
                </Typography>
              </Stack>
              <List sx={{ p: 0 }}>
                <ListItemButton
                  selected={selectedCatalog === ALL_CATALOGS}
                  onClick={() => handleCatalogChange(ALL_CATALOGS)}
                >
                  <ListItemText
                    primary="All catalogs"
                    secondary={`${catalogs.reduce((count, catalog) => count + (catalog.table_count || 0), 0)} tables`}
                  />
                </ListItemButton>
                {catalogs.map((catalog) => (
                  <Box key={catalog.catalog_name}>
                    <ListItemButton
                      selected={selectedCatalog === catalog.catalog_name}
                      onClick={() => handleCatalogChange(catalog.catalog_name)}
                    >
                      <ListItemText
                        primary={catalog.catalog_name}
                        secondary={`${catalog.table_count || 0} tables`}
                      />
                    </ListItemButton>
                    {selectedCatalog === catalog.catalog_name ? (
                      <List disablePadding sx={{ pl: 1 }}>
                        {(catalog.schemas || []).map((schema) => (
                          <ListItemButton
                            key={schema.schema_name}
                            selected={selectedSchema === schema.schema_name}
                            onClick={() => setSelectedSchema(schema.schema_name)}
                            sx={{ minHeight: 38 }}
                          >
                            <ListItemText
                              primary={schema.schema_name}
                              secondary={`${schema.table_count || 0} tables`}
                            />
                          </ListItemButton>
                        ))}
                      </List>
                    ) : null}
                  </Box>
                ))}
              </List>
            </Stack>
          </Paper>

          <Stack spacing={3}>
            {groupedSchemas.length === 0 ? (
              <Paper sx={{ ...panelSx, p: 6, textAlign: "center" }}>
                <Typography variant="h6" fontWeight={800}>
                  No tables found
                </Typography>
                <Typography color="text.secondary" sx={{ mt: 1 }}>
                  Adjust the catalog, schema, or search filters to see managed assets.
                </Typography>
              </Paper>
            ) : null}

            {groupedSchemas.map((catalog) => (
              <Paper key={catalog.catalog_name} sx={{ ...panelSx, overflow: "hidden" }}>
                <Box
                  sx={{
                    px: 3,
                    py: 2.25,
                    borderBottom: `1px solid ${datagateColors.cardBorderSoft}`,
                    background:
                      "linear-gradient(135deg, rgba(30, 64, 175, 0.08) 0%, rgba(248, 250, 252, 1) 65%)",
                  }}
                >
                  <Stack
                    direction={{ xs: "column", md: "row" }}
                    spacing={1.5}
                    justifyContent="space-between"
                  >
                    <Stack spacing={0.5}>
                      <Stack direction="row" spacing={1} alignItems="center">
                        <CatalogIcon color="primary" />
                        <Typography variant="h6" fontWeight={800}>
                          {catalog.catalog_name}
                        </Typography>
                      </Stack>
                      <Typography color="text.secondary">
                        {(catalog.schemas || []).length} schemas • {catalog.table_count || 0} tables
                      </Typography>
                    </Stack>
                  </Stack>
                </Box>

                <Stack spacing={2} sx={{ p: 2 }}>
                  {(catalog.schemas || []).map((schema) => (
                    <Paper
                      key={`${catalog.catalog_name}-${schema.schema_name}`}
                      sx={{
                        borderRadius: 2,
                        border: `1px solid ${datagateColors.cardBorderSoft}`,
                        overflow: "hidden",
                      }}
                    >
                      <Stack
                        direction={{ xs: "column", md: "row" }}
                        spacing={1.5}
                        justifyContent="space-between"
                        alignItems={{ xs: "flex-start", md: "center" }}
                        sx={{ px: 2.5, py: 2, bgcolor: "#F8FAFC" }}
                      >
                        <Stack direction="row" spacing={1} alignItems="center">
                          <SchemaIcon sx={{ color: "primary.main" }} />
                          <Typography fontWeight={800}>{schema.schema_name}</Typography>
                          <Chip size="small" label={`${schema.table_count || 0} tables`} />
                        </Stack>
                      </Stack>

                      <TableContainer>
                        <Table size="small">
                          <TableHead>
                            <TableRow>
                              <TableCell sx={{ bgcolor: "#E2E8F0", color: "#0F172A" }}>Table</TableCell>
                              <TableCell sx={{ bgcolor: "#E2E8F0", color: "#0F172A" }}>Path</TableCell>
                              <TableCell sx={{ bgcolor: "#E2E8F0", color: "#0F172A" }}>Source</TableCell>
                              <TableCell sx={{ bgcolor: "#E2E8F0", color: "#0F172A" }}>Action</TableCell>
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {schema.tables.map((table) => (
                              <TableRow key={table.id} hover>
                                <TableCell sx={{ fontWeight: 800 }}>{table.table_name}</TableCell>
                                <TableCell>
                                  <Typography variant="body2" sx={{ fontFamily: "monospace", color: "text.secondary" }}>
                                    {table.full_name}
                                  </Typography>
                                </TableCell>
                                <TableCell>{table.connection_name}</TableCell>
                                <TableCell>
                                  <Button
                                    size="small"
                                    variant="contained"
                                    onClick={() => {
                                      setSelectedTable(table);
                                      setSection("overview");
                                    }}
                                  >
                                    Open
                                  </Button>
                                </TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </TableContainer>
                    </Paper>
                  ))}
                </Stack>
              </Paper>
            ))}
          </Stack>
        </Box>
      </Stack>
    </Box>
  );
}

export default Explore;
