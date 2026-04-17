import React, { useMemo } from "react";
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
} from "@mui/material";
import {
  ArticleOutlined as DescriptionIcon,
  TableChartOutlined as SampleIcon,
  InsightsOutlined as ObservabilityIcon,
} from "@mui/icons-material";
import TableDescription from "./TableDescription/TableDescription";
import DataSample from "./DataSample/DataSample";
import DataObservability from "./DataObservability/DataObservability";
import { pageShellSx } from "~/theme";

const getOwnerLabel = (owner) =>
  owner?.full_name || owner?.username || owner?.email || "Unassigned owner";

const SECTION_TO_TAB = {
  description: 0,
  sample: 1,
  observability: 2,
};

function TableView({
  assetDetail,
  assetObservability,
  onBack,
  onChangeSampleLimit,
  onChangeSection,
  sampleLimit,
  section = "description",
  observabilityTab = "profile",
}) {
  const ownerLabel = useMemo(() => getOwnerLabel(assetDetail?.owner), [assetDetail?.owner]);
  const activeTab = SECTION_TO_TAB[section] ?? 0;

  const handleTabChange = (_, nextTab) => {
    if (onChangeSection) {
      const nextSection = Object.keys(SECTION_TO_TAB).find((key) => SECTION_TO_TAB[key] === nextTab) || "description";
      onChangeSection(nextSection);
    }
  };

  return (
    <Box sx={pageShellSx}>
      <Box sx={{ mb: 3 }}>
        <Breadcrumbs sx={{ mb: 1 }}>
          <Link underline="hover" color="inherit" onClick={onBack} sx={{ cursor: "pointer" }}>
            Explore
          </Link>
          <Typography color="text.primary">{assetDetail?.table_name}</Typography>
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
        <Tabs value={activeTab} onChange={handleTabChange}>
          <Tab icon={<DescriptionIcon fontSize="small" />} iconPosition="start" label="Description" />
          <Tab icon={<SampleIcon fontSize="small" />} iconPosition="start" label="Data Sample" />
          <Tab icon={<ObservabilityIcon fontSize="small" />} iconPosition="start" label="Observability" />
        </Tabs>
      </Box>

      {activeTab === 0 ? <TableDescription assetDetail={assetDetail} assetObservability={assetObservability} /> : null}
      {activeTab === 1 ? (
        <DataSample assetDetail={assetDetail} onChangeSampleLimit={onChangeSampleLimit} sampleLimit={sampleLimit} />
      ) : null}
      {activeTab === 2 ? (
        <DataObservability
          assetDetail={assetDetail}
          assetObservability={assetObservability}
          initialTab={observabilityTab}
          onTabChange={(nextTab) => onChangeSection?.("observability", nextTab)}
        />
      ) : null}
    </Box>
  );
}

export default TableView;
