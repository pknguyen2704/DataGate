import React from "react";
import { 
  Box, Typography, Paper, Tabs, Tab, Breadcrumbs, Link, 
  Grid, Divider, Skeleton, Stack, Button, Chip
} from "@mui/material";
import { 
  useParams, useNavigate, useLocation, Outlet, Link as RouterLink
} from "react-router-dom";
import { 
  TableChartOutlined, LayersOutlined, DnsOutlined, 
  AccessTimeOutlined, ArrowBack
} from "@mui/icons-material";
import { dataAssetsApi } from "~/apis/dataAssetsApi";
import { useApiResource } from "~/hooks/useApiResource";
import { format } from "date-fns";
import ObservabilityTab from "./Observability/Observability";
import MetricTab from "./Metric/Metric";
import RuleTab from "./Rule/Rule";
import DataQualityTab from "./DataQuality/DataQuality";

export { 
  ObservabilityTab, 
  MetricTab as MetricsTab, 
  RuleTab as RulesTab, 
  DataQualityTab as QualityTab 
};

const TableDetail = () => {
  const { tableId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();

  const tableRes = useApiResource(() => dataAssetsApi.get(tableId), [tableId]);
  const table = tableRes.data;

  const currentTab = location.pathname.split('/').pop();
  
  const handleTabChange = (event, newValue) => {
    navigate(`/app/data-assets/${tableId}/${newValue}`);
  };

  if (tableRes.loading && !table) {
    return (
      <Box sx={{ p: 3 }}>
        <Skeleton variant="text" width={200} height={30} sx={{ mb: 2 }} />
        <Skeleton variant="rectangular" height={150} sx={{ borderRadius: 2, mb: 3 }} />
        <Skeleton variant="rectangular" height={400} sx={{ borderRadius: 2 }} />
      </Box>
    );
  }

  if (tableRes.error) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <Typography color="error">Error loading table details. It may not exist or you lack permission.</Typography>
        <Button onClick={() => navigate('/app/data-assets')} startIcon={<ArrowBack />} sx={{ mt: 2 }}>Back to list</Button>
      </Box>
    );
  }

  return (
    <Box sx={{ p: { xs: 2, md: 3 }, bgcolor: "background.default", flexGrow: 1 }}>
      <Breadcrumbs sx={{ mb: 3 }}>
        <Link component={RouterLink} underline="hover" color="inherit" to="/app/home">Home</Link>
        <Link component={RouterLink} underline="hover" color="inherit" to="/app/data-assets">Data Assets</Link>
        <Typography color="text.primary" sx={{ fontWeight: 600 }}>{table?.table_name || tableId}</Typography>
      </Breadcrumbs>

      <Stack spacing={3}>
        {/* Table Identity Card */}
        <Paper variant="outlined" sx={{ p: 3, borderRadius: 2, position: 'relative', overflow: 'hidden' }}>
          <Box sx={{ position: 'absolute', top: 0, left: 0, width: '4px', height: '100%', bgcolor: 'primary.main' }} />
          
          <Grid container spacing={3} alignItems="center">
            <Grid item xs={12} md={8}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1.5 }}>
                <Box sx={{ p: 1.2, borderRadius: 2, bgcolor: 'primary.light', color: 'primary.main', display: 'flex' }}>
                  <TableChartOutlined />
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                  <Typography variant="h4" fontWeight={800} sx={{ lineHeight: 1.2 }}>{table?.table_name}</Typography>
                  {table && (
                    <Chip
                      size="small"
                      label={table.is_active ? "Active" : "Inactive"}
                      color={table.is_active ? "success" : "default"}
                      variant="outlined"
                      sx={{ borderRadius: 1.5, fontWeight: 600 }}
                    />
                  )}
                </Box>
              </Box>
              
              <Stack direction="row" spacing={2} sx={{ mt: 2 }} flexWrap="wrap" useFlexGap gap={1.5}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.8 }}>
                  <DnsOutlined fontSize="small" color="action" />
                  <Typography variant="body2" fontWeight={600}>{table?.catalog_name}.{table?.schema_name}</Typography>
                </Box>
                <Divider orientation="vertical" flexItem sx={{ height: 16, alignSelf: 'center' }} />
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.8 }}>
                  <AccessTimeOutlined fontSize="small" color="action" />
                  <Typography variant="body2" fontWeight={600}>
                    Latest: {table?.latest_processing_date_hour 
                      ? format(new Date(table.latest_processing_date_hour), "yyyy-MM-dd HH:mm:ss") 
                      : "Never processed"}
                  </Typography>
                </Box>
              </Stack>
            </Grid>
            
          </Grid>
        </Paper>

        {/* Tab Navigation */}
        <Paper variant="outlined" sx={{ borderRadius: 2, bgcolor: 'white' }}>
          <Box sx={{ borderBottom: 1, borderColor: 'divider', px: 2 }}>
            <Tabs 
              value={currentTab} 
              onChange={handleTabChange}
              textColor="primary"
              indicatorColor="primary"
              sx={{
                '& .MuiTab-root': {
                  py: 2,
                  fontWeight: 700,
                  textTransform: 'none',
                  fontSize: '0.95rem',
                  minHeight: 64
                }
              }}
            >
              <Tab label="Observability" value="observability" />
              <Tab label="Metrics" value="metrics" />
              {(table?.schema_name?.toLowerCase() === 'silver' || table?.schema_name?.toLowerCase() === 'gold') && (
                <Tab label="Rules" value="rules" />
              )}
              <Tab label="Data Quality" value="data-quality" />
            </Tabs>
          </Box>
          <Box sx={{ p: 0 }}>
            <Outlet />
          </Box>
        </Paper>
      </Stack>
    </Box>
  );
};

export default TableDetail;
