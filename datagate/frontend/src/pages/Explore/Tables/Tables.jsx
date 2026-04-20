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
  ErrorOutline as IncidentIcon,
} from "@mui/icons-material";
import {
  fetchAssetOverview,
  fetchAssetSample,
} from "~/stores/slices/exploreSlice/index";
import Overview from "./TableDetail/Overview/Overview";
import DataSample from "./TableDetail/DataSample/DataSample";
import DataObservability from "./TableDetail/Observability/Observability";
import Incidents from "./TableDetail/Incidents/Incidents";
import { pageShellSx } from "~/theme";

const getOwnerLabel = (owner) =>
  owner?.full_name || owner?.username || owner?.email || "Unassigned owner";

const SECTION_TO_TAB = {
  overview: 0,
  sample: 1,
  observability: 2,
  incidents: 3,
};

function TableView({
  tableName,
  schemaName,
  connectionId,
  onBack,
  onChangeSection,
  section = "overview",
  observabilityTab = "metadata",
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
    snapshotsByTable,
    volumeTSByTable,
    schemasByTable,
  } = useSelector((state) => state.explore.observability);

  const assetKey = `${connectionId}:${schemaName || 'public'}:${tableName}`;
  const sampleKey = `${connectionId}:${schemaName || 'public'}:${tableName}:${sampleLimit}`;

  const assetDetail = assetOverviewsByKey[assetKey];
  const assetSample = assetSamplesByKey[sampleKey];
  const status = assetOverviewStatusByKey[assetKey];
  const error = assetOverviewErrorByKey[assetKey];

  // Fetch overview
  React.useEffect(() => {
    if (!tableName || !connectionId) return;
    dispatch(fetchAssetOverview({ tableName, schemaName, connectionId }));
  }, [dispatch, tableName, schemaName, connectionId]);

  // Fetch sample
  React.useEffect(() => {
    if (!tableName || !connectionId) return;
    dispatch(fetchAssetSample({ tableName, schemaName, connectionId, sampleLimit }));
  }, [dispatch, tableName, schemaName, connectionId, sampleLimit]);

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
              <Chip size="small" color="primary" variant="outlined" label={`Permitted to: ${ownerLabel}`} />
            </Stack>
            <Stack direction={{ xs: "column", sm: "row" }} spacing={1} alignItems={{ xs: "flex-start", sm: "center" }}>
              <Typography variant="body2" color="text.secondary">
                {assetDetail?.table_name}
              </Typography>
              {assetDetail?.connection_name ? <Chip size="small" label={`Source: ${assetDetail.connection_name}`} variant="outlined" /> : null}
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
          <Tab icon={<IncidentIcon fontSize="small" />} iconPosition="start" label="Incidents" />
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
            initialTab={observabilityTab}
            onTabChange={(nextTab) => onChangeSection?.("observability", nextTab)}
          />
        )}
        {section === "incidents" && (
          <Incidents assetDetail={assetDetail} />
        )}
      </Box>
    </Box>
  );
}

export default TableView;
