import React, { useState, useEffect } from "react";
import { 
  Box, Typography, Paper, Breadcrumbs, Link, Grid, TextField, 
  MenuItem, Table as MuiTable, TableBody, TableCell, TableHead, 
  TableRow, TableContainer, TablePagination, Chip, IconButton,
  Button, Stack, Tooltip
} from "@mui/material";
import { 
  TableChartOutlined, FilterList, Search, Refresh,
  VisibilityOutlined, CheckCircle, Cancel, LayersOutlined
} from "@mui/icons-material";
import { useNavigate, Link as RouterLink } from "react-router-dom";
import { dataAssetsApi } from "~/apis/dataAssetsApi";
import { connectionsApi } from "~/apis/connectionsApi";
import { observabilityApi } from "~/apis/observabilityApi";
import { useApiResource } from "~/hooks/useApiResource";
import { format } from "date-fns";
import { StateBox } from "~/components/DataGate/Page";

const DataAssets = () => {
  const navigate = useNavigate();
  const [filters, setFilters] = useState({
    connection_id: "",
    catalog_name: "",
    schema_name: "",
    is_active: ""
  });
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);

  const connectionsRes = useApiResource(() => connectionsApi.list(), []);
  const variablesRes = useApiResource(() => observabilityApi.getGrafanaVariables(), []);
  
  const tablesRes = useApiResource(() => dataAssetsApi.list({
    ...filters,
    is_active: filters.is_active === "" ? undefined : filters.is_active === "true",
    page: page + 1,
    page_size: pageSize
  }), [filters, page, pageSize]);

  let connections = [];
  if (connectionsRes.data && connectionsRes.data.items) {
    connections = connectionsRes.data.items;
  }

  let catalogs = [];
  let schemas = [];
  if (variablesRes.data) {
    if (variablesRes.data.catalogs) catalogs = variablesRes.data.catalogs;
    if (variablesRes.data.schemas) schemas = variablesRes.data.schemas;
  }

  let tables = [];
  let total = 0;
  if (tablesRes.data) {
    if (tablesRes.data.items) tables = tablesRes.data.items;
    if (tablesRes.data.total) total = tablesRes.data.total;
  }

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({ ...prev, [name]: value }));
    setPage(0); // Reset to first page on filter change
  };

  const handleRowClick = (tableId) => {
    navigate(`/app/data-assets/${tableId}/observability`);
  };

  return (
    <Box sx={{ p: { xs: 2, md: 3 }, bgcolor: "background.default", flexGrow: 1 }}>
      <Breadcrumbs sx={{ mb: 3 }}>
        <Link component={RouterLink} underline="hover" color="inherit" to="/app/home" sx={{ display: 'flex', alignItems: 'center' }}>
          Home
        </Link>
        <Typography color="text.primary" sx={{ display: 'flex', alignItems: 'center', fontWeight: 600 }}>
          Data Assets
        </Typography>
      </Breadcrumbs>
      
      <Stack spacing={3}>
        {/* Header Section */}
        <Paper variant="outlined" sx={{ p: 2.5, borderRadius: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Box sx={{ p: 1, borderRadius: 1.5, bgcolor: 'primary.light', color: 'primary.main', display: 'flex' }}>
              <TableChartOutlined />
            </Box>
            <Box>
              <Typography variant="h5" fontWeight={800}>Data Assets</Typography>
              <Typography variant="body2" color="text.secondary">Manage and monitor your data lake tables.</Typography>
            </Box>
          </Box>
          <Button 
            variant="contained" 
            startIcon={<Refresh />} 
            onClick={() => {
              tablesRes.reload();
              variablesRes.reload();
            }}
            sx={{ borderRadius: 2, px: 3 }}
          >
            Refresh
          </Button>
        </Paper>

        {/* Filters Section */}
        <Paper variant="outlined" sx={{ p: 2.5, borderRadius: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <FilterList fontSize="small" color="action" />
            <Typography variant="subtitle2" fontWeight={700}>Filters</Typography>
          </Box>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                select
                fullWidth
                size="small"
                label="Connection"
                name="connection_id"
                value={filters.connection_id}
                onChange={handleFilterChange}
                sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
              >
                <MenuItem value="">All Connections</MenuItem>
                {connections.map(c => <MenuItem key={c.id} value={c.id}>{c.connection_name}</MenuItem>)}
              </TextField>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                select
                fullWidth
                size="small"
                label="Catalog"
                name="catalog_name"
                value={filters.catalog_name}
                onChange={handleFilterChange}
                sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
              >
                <MenuItem value="">All Catalogs</MenuItem>
                {catalogs.map(c => <MenuItem key={c} value={c}>{c}</MenuItem>)}
              </TextField>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                select
                fullWidth
                size="small"
                label="Schema"
                name="schema_name"
                value={filters.schema_name}
                onChange={handleFilterChange}
                sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
              >
                <MenuItem value="">All Schemas</MenuItem>
                {schemas.map(s => <MenuItem key={s} value={s}>{s}</MenuItem>)}
              </TextField>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                select
                fullWidth
                size="small"
                label="Status"
                name="is_active"
                value={filters.is_active}
                onChange={handleFilterChange}
                sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
              >
                <MenuItem value="">All Status</MenuItem>
                <MenuItem value="true">Active</MenuItem>
                <MenuItem value="false">Inactive</MenuItem>
              </TextField>
            </Grid>
          </Grid>
        </Paper>

        {/* Table List Section */}
        <StateBox 
          loading={tablesRes.loading} 
          error={tablesRes.error} 
          empty={!tables.length}
          onReload={tablesRes.reload}
        >
          <TableContainer component={Paper} variant="outlined" sx={{ borderRadius: 2, overflow: 'hidden' }}>
            <MuiTable>
              <TableHead>
                <TableRow>
                  <TableCell>Table Name</TableCell>
                  <TableCell>Catalog / Schema</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Latest Processed</TableCell>
                  <TableCell align="right">Action</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {tables.map((table) => (
                  <TableRow 
                    key={table.id} 
                    hover 
                    onClick={() => handleRowClick(table.id)}
                    sx={{ cursor: 'pointer', '&:last-child td, &:last-child th': { border: 0 } }}
                  >
                    <TableCell>
                      <Typography variant="body2" fontWeight={600} color="primary.main">{table.table_name}</Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="caption" color="text.secondary">{table.catalog_name} / {table.schema_name}</Typography>
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={table.is_active ? "Active" : "Inactive"} 
                        size="small" 
                        variant="filled"
                        color={table.is_active ? "success" : "default"}
                        icon={table.is_active ? <CheckCircle sx={{ color: 'white !important' }} /> : <Cancel />}
                        sx={{ 
                          fontWeight: 700, 
                          borderRadius: 1.5,
                          ...(table.is_active && {
                            bgcolor: 'success.main',
                            color: 'white',
                          })
                        }}
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary">
                        {table.latest_processing_date_hour 
                          ? format(new Date(table.latest_processing_date_hour), "yyyy-MM-dd HH:mm:ss") 
                          : "No batch data"}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Tooltip title="View Details">
                        <IconButton size="small" color="primary">
                          <VisibilityOutlined fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </MuiTable>
            <TablePagination
              rowsPerPageOptions={[5, 10, 25, 50]}
              component="div"
              count={total}
              rowsPerPage={pageSize}
              page={page}
              onPageChange={(e, newPage) => setPage(newPage)}
              onRowsPerPageChange={(e) => {
                setPageSize(parseInt(e.target.value, 10));
                setPage(0);
              }}
            />
          </TableContainer>
        </StateBox>
      </Stack>
    </Box>
  );
};

export default DataAssets;
