import React, { useEffect, useMemo, useState } from "react";
import {
  Box,
  Breadcrumbs,
  Button,
  Chip,
  CircularProgress,
  Link,
  Stack,
  Tab,
  Tabs,
  Typography,
} from "@mui/material";
import {
  RuleOutlined as RuleIcon,
  WarningAmberRounded as IncidentIcon,
} from "@mui/icons-material";
import { useLocation, useNavigate } from "react-router-dom";
import { servicesApi } from "~/apis/services";
import RulesList from "./RulesList/RulesList";
import Incidents from "./Incidents/Incidents";

const getOwnerLabel = (owner) =>
  owner?.full_name || owner?.username || owner?.email || "Unassigned owner";

const Rules = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const searchParams = useMemo(() => new URLSearchParams(location.search), [location.search]);
  const tableParam = searchParams.get("table");
  const serviceParam = searchParams.get("service");
  const tabParam = searchParams.get("tab");

  const [activeTab, setActiveTab] = useState(tabParam === "incidents" ? 1 : 0);
  const [assetDetail, setAssetDetail] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setActiveTab(tabParam === "incidents" ? 1 : 0);
  }, [tabParam]);

  useEffect(() => {
    if (!tableParam || !serviceParam) {
      setAssetDetail(null);
      return;
    }

    const fetchAssetDetail = async () => {
      try {
        setLoading(true);
        const response = await servicesApi.getAssetDetail(tableParam, Number(serviceParam));
        setAssetDetail(response.data);
      } catch (error) {
        console.error("Failed to fetch asset detail:", error);
        setAssetDetail(null);
      } finally {
        setLoading(false);
      }
    };

    fetchAssetDetail();
  }, [serviceParam, tableParam]);

  const handleTabChange = (_, nextTab) => {
    setActiveTab(nextTab);
    const params = new URLSearchParams(location.search);
    params.set("tab", nextTab === 1 ? "incidents" : "rules");
    navigate(`/rules?${params.toString()}`, { replace: true });
  };

  if (!tableParam || !serviceParam) {
    return (
      <Box sx={{ p: 4, height: "100%", overflow: "auto", textAlign: "center" }}>
        <Typography variant="h4" fontWeight={800} sx={{ mb: 0.5 }}>
          Rules & Incidents
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Select a table from Explore or Observability to manage rules and review incidents.
        </Typography>
        <Button variant="contained" sx={{ mt: 3 }} onClick={() => navigate("/explore")}>
          Go to Assets
        </Button>
      </Box>
    );
  }

  const ownerLabel = getOwnerLabel(assetDetail?.owner);
  const assetName = assetDetail?.asset_name || tableParam.split(".").pop();

  return (
    <Box sx={{ p: 4, height: "100%", overflow: "auto" }}>
      <Box sx={{ mb: 3 }}>
        <Breadcrumbs sx={{ mb: 1 }}>
          <Link underline="hover" color="inherit" onClick={() => navigate("/explore")} sx={{ cursor: "pointer" }}>
            Explore
          </Link>
          <Typography color="text.primary">{tableParam}</Typography>
        </Breadcrumbs>

        {loading ? (
          <Stack direction="row" spacing={1.5} alignItems="center">
            <CircularProgress size={20} />
            <Typography color="text.secondary">Loading table context...</Typography>
          </Stack>
        ) : (
          <Stack spacing={1.5}>
            <Stack direction={{ xs: "column", sm: "row" }} spacing={1.5} alignItems={{ xs: "flex-start", sm: "center" }}>
              <Typography variant="h4" sx={{ fontWeight: 800 }}>
                {assetName}
              </Typography>
              <Chip
                size="small"
                color="primary"
                variant="outlined"
                label={`Owner: ${ownerLabel}`}
                sx={{ fontWeight: 700, maxWidth: "100%" }}
              />
            </Stack>
            <Stack direction={{ xs: "column", sm: "row" }} spacing={1} alignItems={{ xs: "flex-start", sm: "center" }}>
              <Typography variant="body2" color="text.secondary">
                {tableParam}
              </Typography>
              {assetDetail?.service_name ? (
                <Chip size="small" label={assetDetail.service_name} variant="outlined" />
              ) : null}
            </Stack>
          </Stack>
        )}
      </Box>

      <Box sx={{ borderBottom: 1, borderColor: "divider", mb: 3 }}>
        <Tabs value={activeTab} onChange={handleTabChange}>
          <Tab icon={<RuleIcon fontSize="small" />} iconPosition="start" label="Rules" />
          <Tab icon={<IncidentIcon fontSize="small" />} iconPosition="start" label="Incidents" />
        </Tabs>
      </Box>

      {activeTab === 0 ? (
        <RulesList assetDetail={assetDetail} tableName={tableParam} />
      ) : (
        <Incidents assetDetail={assetDetail} tableName={tableParam} />
      )}
    </Box>
  );
};

export default Rules;
