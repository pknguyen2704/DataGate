import React, { useEffect, useState } from "react";
import { Box, Button, Chip, Stack, Tab, Tabs, Typography, Switch, FormControlLabel } from "@mui/material";
import {
  PlayCircleOutline as RunIcon,
  Assessment as MetadataIcon,
  Warning as IncidentIcon,
} from "@mui/icons-material";
import { toast } from "react-toastify";
import { useDispatch, useSelector } from "react-redux";
import {
  fetchSnapshots,
  fetchVolumeTS,
  fetchSchema,
  fetchIncidents,
  fetchVolumePrediction,
  fetchFreshnessPrediction,
  fetchSchemaHistory,
} from "~/stores/slices/exploreSlice/index";
import { observabilityApi } from "~/apis/observability";

import Metadata from "./Metadata/Metadata.jsx";
import IncidentList from "./Incidents/Incidents.jsx";

const TABS = ["metadata", "incidents"];

function DataObservability({ assetDetail, assetObservability, initialTab = "metadata", onTabChange }) {
  const dispatch = useDispatch();
  const [activeTab, setActiveTab] = useState(0);
  const [isManualRunning, setIsManualRunning] = useState(false);
  const [isHourlyActive, setIsHourlyActive] = useState(false);
  const [isConfigLoading, setIsConfigLoading] = useState(false);

  const tableName = assetDetail?.table_name;
  const schemaName = assetDetail?.schema_name;

  const {
    snapshotsByTable,
    volumeTSByTable,
    incidentsByTable,
    volumePredictionByTable,
    freshnessPredictionByTable,
    schemaHistoryByTable,
  } = useSelector((state) => state.explore.observability);

  // Fetch all observability data when table changes
  useEffect(() => {
    if (!tableName) return;
    dispatch(fetchSnapshots({ tableName, schemaName }));
    dispatch(fetchVolumeTS({ tableName, schemaName }));
    dispatch(fetchSchema({ tableName, schemaName }));
    dispatch(fetchIncidents({ tableName, schemaName }));
    dispatch(fetchVolumePrediction({ tableName, schemaName }));
    dispatch(fetchFreshnessPrediction({ tableName, schemaName }));
    dispatch(fetchSchemaHistory({ tableName, schemaName }));
  }, [dispatch, tableName, schemaName]);

  useEffect(() => {
    const index = TABS.indexOf(initialTab);
    setActiveTab(index >= 0 ? index : 0);
  }, [initialTab]);

  // Fetch config for toggle
  useEffect(() => {
    if (!assetDetail?.asset_name) return;
    const fetchConfig = async () => {
      try {
        const res = await observabilityApi.getConfig({
          catalog: "iceberg",
          schema: assetDetail?.schema_name || "public",
          table: assetDetail?.asset_name,
        });
        setIsHourlyActive(res.data?.is_active || false);
      } catch (e) {
        console.error("Failed to fetch config", e);
      }
    };
    fetchConfig();
  }, [assetDetail]);

  const handleToggleHourly = async (e) => {
    const newStatus = e.target.checked;
    setIsHourlyActive(newStatus);
    setIsConfigLoading(true);
    try {
      await observabilityApi.updateConfig({
        catalog: "iceberg",
        schema_name: assetDetail?.schema_name || "public",
        table_name: assetDetail?.asset_name,
        is_active: newStatus,
      });
      toast.success(`Đã ${newStatus ? "bật" : "tắt"} tự động quét hàng giờ.`);
    } catch (error) {
      toast.error("Lỗi khi cập nhật cấu hình.");
      setIsHourlyActive(!newStatus); // revert
    } finally {
      setIsConfigLoading(false);
    }
  };

  const handleRunNow = async () => {
    if (!assetDetail?.asset_name) return;
    try {
      setIsManualRunning(true);
      await observabilityApi.triggerScan({
        catalog: "iceberg",
        schema_name: assetDetail?.schema_name || "public",
        table_name: assetDetail?.asset_name,
      });
      toast.success("🚀 Đã bắt đầu quét metadata cho bảng " + assetDetail?.asset_name);
    } catch (error) {
      toast.error("❌ Lỗi khi kích hoạt quét dữ liệu.");
    } finally {
      setIsManualRunning(false);
    }
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
    if (onTabChange) onTabChange(TABS[newValue]);
  };

  const fullTableName = `${schemaName || "public"}.${tableName}`;

  const incidents = incidentsByTable[fullTableName] || [];
  const openIncidents = incidents.filter((i) => i.status === "open");

  return (
    <Box>
      <Stack direction="row" spacing={2} justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
        <Box sx={{ borderBottom: 1, borderColor: "divider", flex: 1 }}>
          <Tabs
            value={activeTab}
            onChange={handleTabChange}
            sx={{
              "& .MuiTab-root": { textTransform: "none", fontWeight: 600, fontSize: 13, minHeight: 42 },
            }}
          >
            <Tab icon={<MetadataIcon sx={{ fontSize: 18 }} />} iconPosition="start" label="Metadata & Prediction" />
            <Tab
              icon={<IncidentIcon sx={{ fontSize: 18 }} />}
              iconPosition="start"
              label={
                <Stack direction="row" spacing={0.5} alignItems="center">
                  <span>Incidents</span>
                  {openIncidents.length > 0 && (
                    <Chip
                      label={openIncidents.length}
                      size="small"
                      color="error"
                      sx={{ height: 18, fontSize: 11, fontWeight: 700 }}
                    />
                  )}
                </Stack>
              }
            />
          </Tabs>
        </Box>

        <Stack direction="row" spacing={2} alignItems="center">
          <FormControlLabel
            control={
              <Switch
                checked={isHourlyActive}
                onChange={handleToggleHourly}
                disabled={isConfigLoading}
                color="secondary"
                size="small"
              />
            }
            label={
              <Typography variant="body2" sx={{ fontWeight: 500, fontSize: 13 }}>
                Auto (Hourly)
              </Typography>
            }
            sx={{ m: 0 }}
          />
          <Button
            variant="contained"
            size="small"
            startIcon={<RunIcon />}
            onClick={handleRunNow}
            disabled={isManualRunning}
            sx={{
              textTransform: "none",
              borderRadius: 2,
              px: 2,
              fontSize: 13,
              background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
              "&:hover": { background: "linear-gradient(135deg, #5a6fd6 0%, #6a4190 100%)" },
            }}
          >
            {isManualRunning ? "Scanning..." : "Run Scan"}
          </Button>
        </Stack>
      </Stack>

      <Box sx={{ py: 1 }}>
        {activeTab === 0 && (
          <Metadata
            snapshots={snapshotsByTable[fullTableName] || []}
            freshnessPrediction={freshnessPredictionByTable[fullTableName]}
            volumeData={volumeTSByTable[fullTableName] || []}
            volumePrediction={volumePredictionByTable[fullTableName]}
            schemaHistory={schemaHistoryByTable[fullTableName]}
            tableName={fullTableName}
          />
        )}

        {activeTab === 1 && (
          <IncidentList incidents={incidents} tableName={tableName} />
        )}
      </Box>
    </Box>
  );
}

export default DataObservability;
