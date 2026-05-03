import React, { useEffect, useMemo, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import {
  Alert,
  Box,
  Breadcrumbs,
  Button,
  Chip,
  CircularProgress,
  Link,
  Paper,
  Stack,
  Tab,
  Tabs,
  Typography,
} from "@mui/material";
import {
  ArticleOutlined as DescriptionIcon,
  InsightsOutlined as AnomalyIcon,
  LockOutlined as LockIcon,
  RuleOutlined as RuleIcon,
  TableChartOutlined as SampleIcon,
} from "@mui/icons-material";
import { fetchAssetOverview, fetchAssetSample } from "~/stores/slices/tableSlice";
import { datagateColors, pageShellSx, panelSx } from "~/theme";
import DataSample from "./DataSample/DataSample";
import Overview from "./Overview/Overview";
import RulesManagement from "./Rule/Rule";
import AnomalyDetection from "./AnomalyDetection/AnomalyDetection";

const SECTION_TO_TAB = {
  overview: 0,
  sample: 1,
  rules: 2,
  anomaly: 3,
};

const getAssetKey = ({ tableName, schemaName, catalogName }) =>
  `${catalogName || "default"}:${schemaName || "public"}:${tableName}`;

const getSampleKey = ({ tableName, schemaName, catalogName, sampleLimit }) =>
  `${getAssetKey({ tableName, schemaName, catalogName })}:${sampleLimit}`;

const getOwnerLabel = (owner) =>
  owner?.full_name || owner?.username || owner?.email || "Unassigned owner";

function TableDetail({
  tableId,
  tableName,
  schemaName,
  catalogName,
  onBack,
  onChangeSection,
  onNavigateCrumb,
  section = "overview",
}) {
  const dispatch = useDispatch();
  const [sampleLimit, setSampleLimit] = useState(50);
  const currentUser = useSelector((state) => state.auth.user);
  const isSuperuser = currentUser?.is_superuser;
  const accessibleTables = currentUser?.accessible_tables || [];
  const {
    assetOverviewsByKey,
    assetOverviewStatusByKey,
    assetOverviewErrorByKey,
    assetSamplesByKey,
    assetSampleStatusByKey,
    assetSampleErrorByKey,
  } = useSelector((state) => state.explore.overview);

  const fullTableName = catalogName ? `${catalogName}.${schemaName}.${tableName}` : `${schemaName}.${tableName}`;
  const hasAccess = useMemo(() => {
    if (isSuperuser) return true;
    if (accessibleTables.length === 0 && !isSuperuser) return true;
    return accessibleTables.includes(fullTableName);
  }, [accessibleTables, fullTableName, isSuperuser]);

  const assetKey = getAssetKey({ tableName, schemaName, catalogName });
  const sampleKey = getSampleKey({ tableName, schemaName, catalogName, sampleLimit });
  const assetDetail = assetOverviewsByKey[assetKey];
  const assetSample = assetSamplesByKey[sampleKey];
  const status = assetOverviewStatusByKey[assetKey];
  const error = assetOverviewErrorByKey[assetKey];
  const sampleStatus = assetSampleStatusByKey[sampleKey];
  const sampleError = assetSampleErrorByKey[sampleKey];

  useEffect(() => {
    if (!tableName || !schemaName || !catalogName || !hasAccess) return;
    dispatch(fetchAssetOverview({ tableName, schemaName, catalogName }));
  }, [catalogName, dispatch, hasAccess, schemaName, tableName]);

  useEffect(() => {
    if (!tableName || !schemaName || !catalogName || !hasAccess) return;
    dispatch(fetchAssetSample({ tableName, schemaName, catalogName, sampleLimit }));
  }, [catalogName, dispatch, hasAccess, sampleLimit, schemaName, tableName]);

  const ownerLabel = useMemo(() => getOwnerLabel(assetDetail?.owner), [assetDetail?.owner]);
  const activeTab = SECTION_TO_TAB[section] ?? 0;

  if (!hasAccess) {
    return (
      <Box sx={{ ...pageShellSx, display: "flex", alignItems: "center", justifyContent: "center", minHeight: "60vh" }}>
        <Paper sx={{ ...panelSx, p: 6, textAlign: "center", maxWidth: 480 }}>
          <LockIcon sx={{ fontSize: 64, color: "error.main", mb: 2, opacity: 0.85 }} />
          <Typography variant="h5" fontWeight={900} gutterBottom>
            Access denied
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
            You do not have permission to view <strong>{fullTableName}</strong>.
          </Typography>
          <Button variant="contained" onClick={onBack}>
            Back to Explore
          </Button>
        </Paper>
      </Box>
    );
  }

  if (status === "loading" && !assetDetail) {
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

  const detail = assetDetail || {
    id: tableId,
    asset_name: tableName,
    catalog_name: catalogName,
    schema_name: schemaName,
    table_name: tableName,
    full_name: fullTableName,
    columns: [],
  };

  return (
    <Box sx={pageShellSx}>
      <Stack spacing={3}>
        <Paper
          sx={{
            ...panelSx,
            p: 3,
            background:
              "linear-gradient(135deg, rgba(37, 99, 235, 0.12) 0%, rgba(255, 255, 255, 0.92) 60%, rgba(248, 250, 252, 1) 100%)",
          }}
        >
          <Stack spacing={2}>
            <Breadcrumbs>
              <Link
                underline="hover"
                color="inherit"
                onClick={() => onNavigateCrumb?.({}) ?? onBack?.()}
                sx={{ cursor: "pointer", fontWeight: 700 }}
              >
                Explore
              </Link>
              <Link
                underline="hover"
                color="inherit"
                onClick={() => onNavigateCrumb?.({ catalogName: detail.catalog_name })}
                sx={{ cursor: "pointer", fontWeight: 700 }}
              >
                {detail.catalog_name}
              </Link>
              <Link
                underline="hover"
                color="inherit"
                onClick={() =>
                  onNavigateCrumb?.({
                    catalogName: detail.catalog_name,
                    schemaName: detail.schema_name,
                  })
                }
                sx={{ cursor: "pointer", fontWeight: 700 }}
              >
                {detail.schema_name}
              </Link>
              <Typography color="text.primary" sx={{ fontWeight: 800 }}>
                {detail.asset_name}
              </Typography>
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
                    {detail.asset_name}
                  </Typography>
                  <Chip size="small" label={detail.connection_name || "Managed source"} color="primary" variant="outlined" />
                  <Chip size="small" color="primary" variant="outlined" label={ownerLabel} />
                </Stack>
                <Typography
                  variant="body2"
                  sx={{ color: "text.secondary", fontFamily: "monospace" }}
                >
                  {detail.full_name || [detail.catalog_name, detail.schema_name, detail.table_name].filter(Boolean).join(".")}
                </Typography>
              </Stack>

              <Button variant="outlined" onClick={onBack}>
                Back to Explore
              </Button>
            </Stack>
          </Stack>
        </Paper>

        <Paper sx={{ ...panelSx, p: 1, borderColor: datagateColors.cardBorder }}>
          <Tabs
            value={activeTab}
            onChange={(_, nextTab) => {
              const nextSection =
                Object.keys(SECTION_TO_TAB).find((key) => SECTION_TO_TAB[key] === nextTab) || "overview";
              onChangeSection?.(nextSection);
            }}
          >
            <Tab icon={<DescriptionIcon fontSize="small" />} iconPosition="start" label="Overview" />
            <Tab icon={<SampleIcon fontSize="small" />} iconPosition="start" label="Data Sample" />
            <Tab icon={<RuleIcon fontSize="small" />} iconPosition="start" label="Rules" />
            <Tab icon={<AnomalyIcon fontSize="small" />} iconPosition="start" label="Anomaly" />
          </Tabs>
        </Paper>

        {section === "overview" ? (
          <Overview assetDetail={detail} tableId={detail.id || tableId} />
        ) : null}

        {section === "sample" ? (
          <DataSample
            assetSample={assetSample}
            sampleStatus={sampleStatus}
            sampleError={sampleError}
            onChangeSampleLimit={(limit) => setSampleLimit(limit)}
            sampleLimit={sampleLimit}
          />
        ) : null}

        {section === "rules" ? (
          <RulesManagement
            tableId={detail.id || tableId}
            columns={detail.columns || []}
          />
        ) : null}

        {section === "anomaly" ? (
          <AnomalyDetection
            tableId={detail.id || tableId}
            assetDetail={detail}
          />
        ) : null}
      </Stack>
    </Box>
  );
}

export default TableDetail;
