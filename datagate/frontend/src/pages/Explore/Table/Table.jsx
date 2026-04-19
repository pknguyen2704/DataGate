import React, { useMemo } from "react";
import { useDispatch, useSelector } from "react-redux";
import {
  Box,
  Breadcrumbs,
  Button,
  Chip,
  Link,
  Stack,
  Tab,
  Tabs,
  Typography,
  Alert,
  CircularProgress,
} from "@mui/material";
import {
  ArticleOutlined as DescriptionIcon,
  TableChartOutlined as SampleIcon,
  InsightsOutlined as ObservabilityIcon,
  Rule as QualityIcon,
} from "@mui/icons-material";
import {
  fetchAssetOverview,
  fetchAssetSample,
} from "~/stores/slices/exploreSlice/index";
import Overview from "./Overview/Overview";
import DataSample from "./DataSample/DataSample";
import DataObservability from "./DataObservability/DataObservability";
import MetricsMonitoring from "./MetricsMonitoring/MetricsMonitoring";
import { pageShellSx } from "~/theme";

const getOwnerLabel = (owner) =>
  owner?.full_name || owner?.username || owner?.email || "Unassigned owner";

const SECTION_TO_TAB = {
  overview: 0,
  sample: 1,
  observability: 2,
  quality: 3,
};

function TableView({
  tableName,
  schemaName,
  serviceId,
  onBack,
  onChangeSection,
  section = "overview",
  observabilityTab = "profile",
}) {
  const dispatch = useDispatch();
  const [sampleLimit, setSampleLimit] = React.useState(50);

  const {
    assetOverviewsByKey,
    assetOverviewStatusByKey,
    assetOverviewErrorByKey,
    assetSamplesByKey,
  } = useSelector((state) => state.explore.overview);

  const {
    incidentsByTable,
    schemasByTable,
    snapshotsByTable,
    volumeTSByTable,
  } = useSelector((state) => state.explore.observability);

  const assetKey = `${serviceId}:${schemaName || 'public'}:${tableName}`;
  const sampleKey = `${serviceId}:${schemaName || 'public'}:${tableName}:${sampleLimit}`;

  const assetDetail = assetOverviewsByKey[assetKey];
  const assetSample = assetSamplesByKey[sampleKey];
  const status = assetOverviewStatusByKey[assetKey];
  const error = assetOverviewErrorByKey[assetKey];

  // Fetch overview chỉ khi đổi bảng/service
  React.useEffect(() => {
    if (!tableName || !serviceId) return;
    dispatch(fetchAssetOverview({ tableName, schemaName, serviceId }));
  }, [dispatch, tableName, schemaName, serviceId]);

  // Fetch sample khi đổi bảng/service HOẶC sampleLimit
  React.useEffect(() => {
    if (!tableName || !serviceId) return;
    dispatch(fetchAssetSample({ tableName, schemaName, serviceId, sampleLimit }));
  }, [dispatch, tableName, schemaName, serviceId, sampleLimit]);

  const ownerLabel = useMemo(() => getOwnerLabel(assetDetail?.owner), [assetDetail?.owner]);
  const activeTab = SECTION_TO_TAB[section] ?? 0;

  if (status === "loading") {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", py: 10 }}>
        <CircularProgress size={32} />
      </Box>
    );
  }

  if (status === "failed") {
    return <Alert severity="error" sx={{ m: 3 }}>{error}</Alert>;
  }

  if (!assetDetail && status === "succeeded") {
    return <Alert severity="warning" sx={{ m: 3 }}>Asset not found.</Alert>;
  }

  const fullTableName = `${schemaName || 'public'}.${tableName}`;
  const assetObservability = {
    incidents: incidentsByTable[fullTableName] || [],
    schema: schemasByTable[fullTableName] || [],
    snapshots: snapshotsByTable[fullTableName] || [],
    volume: volumeTSByTable[fullTableName] || [],
  };

  return (
    <Box sx={pageShellSx}>
      <Box sx={{ mb: 3 }}>
        <Breadcrumbs sx={{ mb: 1 }}>
          <Link underline="hover" color="inherit" onClick={onBack} sx={{ cursor: "pointer" }}>
            Explore
          </Link>
          <Typography color="inherit">{assetDetail?.schema_name}</Typography>
          <Typography color="text.primary" sx={{ fontWeight: 600 }}>{assetDetail?.asset_name}</Typography>
        </Breadcrumbs>

        <Stack
          direction={{ xs: "column", lg: "row" }}
          spacing={2}
          justifyContent="space-between"
          alignItems={{ xs: "flex-start", lg: "center" }}
        >
          <Stack spacing={1.5}>
            <Stack direction={{ xs: "column", sm: "row" }} spacing={1.5} alignItems={{ xs: "flex-start", sm: "center" }}>
              <Typography variant="h4" fontWeight={800}>
                {assetDetail?.asset_name}
              </Typography>
              <Chip size="small" color="primary" variant="outlined" label={`Owner: ${ownerLabel}`} />
            </Stack>
            <Stack direction={{ xs: "column", sm: "row" }} spacing={1} alignItems={{ xs: "flex-start", sm: "center" }}>
              <Typography variant="body2" color="text.secondary">
                {assetDetail?.table_name}
              </Typography>
              {assetDetail?.service_name ? <Chip size="small" label={assetDetail.service_name} variant="outlined" /> : null}
              {assetDetail?.service_type ? <Chip size="small" label={assetDetail.service_type} variant="outlined" /> : null}
            </Stack>
          </Stack>

          <Button variant="outlined" onClick={onBack}>
            Back to Explore
          </Button>
        </Stack>
      </Box>

      <Box sx={{ borderBottom: 1, borderColor: "divider", mb: 3 }}>
        <Tabs value={activeTab} onChange={(_, nextTab) => {
          const nextSection = Object.keys(SECTION_TO_TAB).find((key) => SECTION_TO_TAB[key] === nextTab) || "overview";
          onChangeSection?.(nextSection);
        }}>
          <Tab icon={<DescriptionIcon fontSize="small" />} iconPosition="start" label="Overview" />
          <Tab icon={<SampleIcon fontSize="small" />} iconPosition="start" label="Data Sample" />
          <Tab icon={<ObservabilityIcon fontSize="small" />} iconPosition="start" label="Observability" />
          <Tab icon={<QualityIcon fontSize="small" />} iconPosition="start" label="Quality Metrics" />
        </Tabs>
      </Box>

      <Box sx={{ py: 1 }}>
        {section === "overview" && <Overview assetDetail={assetDetail} assetObservability={assetObservability} />}
        {section === "sample" && (
          <DataSample
            assetSample={assetSample}
            onChangeSampleLimit={(limit) => setSampleLimit(limit)}
            sampleLimit={sampleLimit}
          />
        )}
        {section === "observability" && (
          <DataObservability
            assetDetail={assetDetail}
            assetObservability={assetObservability}
            initialTab={observabilityTab}
            onTabChange={(nextTab) => onChangeSection?.("observability", nextTab)}
          />
        )}
        {section === "quality" && (
          <MetricsMonitoring assetDetail={assetDetail} />
        )}
      </Box>
    </Box>
  );
}

export default TableView;
