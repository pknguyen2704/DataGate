import React, { useMemo, useEffect, useState } from "react";
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
  Paper,
} from "@mui/material";
import {
  ArticleOutlined as DescriptionIcon,
  TableChartOutlined as SampleIcon,
  InsightsOutlined as ObservabilityIcon,
  ErrorOutline as IncidentIcon,
  LockOutlined as LockIcon,
} from "@mui/icons-material";
import {
  fetchAssetOverview,
  fetchAssetSample,
} from "~/stores/slices/exploreSlice/index";
import Overview from "./Overview/Overview";
import DataSample from "./DataSample/DataSample";
import DataObservability from "./Observability/Observability";
import Incidents from "./Incidents/Incidents";
import { pageShellSx } from "~/theme";

const getOwnerLabel = (owner) =>
  owner?.full_name || owner?.username || owner?.email || "Unassigned owner";

const SECTION_TO_TAB = {
  overview: 0,
  sample: 1,
  observability: 2,
  incidents: 3,
};

function TableDetail({
  tableName,
  schemaName,
  connectionId,
  onBack,
  onChangeSection,
  section = "overview",
  observabilityTab = "metadata",
}) {
  const dispatch = useDispatch();
  const [sampleLimit, setSampleLimit] = useState(50);

  // RBAC state
  const currentUser = useSelector((state) => state.auth.user);
  const isSuperuser = currentUser?.is_superuser;
  const accessibleTables = currentUser?.accessible_tables || [];

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

  // Check Access
  const fullTableName = schemaName ? `${schemaName}.${tableName}` : tableName;
  const hasAccess = useMemo(() => {
    if (isSuperuser) return true;
    return accessibleTables.includes(fullTableName);
  }, [isSuperuser, accessibleTables, fullTableName]);

  const assetKey = `${connectionId}:${schemaName || 'public'}:${tableName}`;
  const sampleKey = `${connectionId}:${schemaName || 'public'}:${tableName}:${sampleLimit}`;

  const assetDetail = assetOverviewsByKey[assetKey];
  const assetSample = assetSamplesByKey[sampleKey];
  const status = assetOverviewStatusByKey[assetKey];
  const error = assetOverviewErrorByKey[assetKey];

  // Fetch overview
  useEffect(() => {
    if (!tableName || !connectionId || !hasAccess) return;
    dispatch(fetchAssetOverview({ tableName, schemaName, connectionId }));
  }, [dispatch, tableName, schemaName, connectionId, hasAccess]);

  // Fetch sample
  useEffect(() => {
    if (!tableName || !connectionId || !hasAccess) return;
    dispatch(fetchAssetSample({ tableName, schemaName, connectionId, sampleLimit }));
  }, [dispatch, tableName, schemaName, connectionId, sampleLimit, hasAccess]);

  const ownerLabel = useMemo(() => getOwnerLabel(assetDetail?.owner), [assetDetail?.owner]);
  const activeTab = SECTION_TO_TAB[section] ?? 0;

  // --- ACCESS DENIED UI ---
  if (!hasAccess) {
    return (
      <Box sx={{ ...pageShellSx, display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <Paper elevation={0} sx={{ p: 6, textAlign: 'center', borderRadius: 4, border: '1px solid #fee2e2', bgcolor: '#fff' }}>
          <LockIcon sx={{ fontSize: 64, color: 'error.main', mb: 2, opacity: 0.8 }} />
          <Typography variant="h5" fontWeight={900} gutterBottom>Access Denied</Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 4, maxWidth: 400 }}>
            You do not have permission to view the data for <b>{fullTableName}</b>. 
            Please contact your administrator to request access.
          </Typography>
          <Button variant="contained" onClick={onBack} sx={{ borderRadius: 2, px: 4 }}>
            Go Back
          </Button>
        </Paper>
      </Box>
    );
  }

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

  const normalizedObsKey = `${schemaName || 'public'}.${tableName}`;
  const assetObservability = {
    schema: schemasByTable[normalizedObsKey] || [],
    snapshots: snapshotsByTable[normalizedObsKey] || [],
    volume: volumeTSByTable[normalizedObsKey] || [],
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

export default TableDetail;