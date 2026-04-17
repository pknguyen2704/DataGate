import React, { useEffect, useMemo, useState } from "react";
import {
  Alert,
  Box,
  Button,
  Chip,
  Drawer,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  Tab,
  Tabs,
  TextField,
  Typography,
} from "@mui/material";
import {
  AutoFixHighOutlined as MlIcon,
  PlayCircleOutline as RunIcon,
  SettingsApplicationsOutlined as ConfigIcon,
  TableChartOutlined as MetadataIcon,
} from "@mui/icons-material";
import { toast } from "react-toastify";
import { observabilityApi } from "~/apis/observability";
import { subtlePanelSx } from "~/theme";
import Profile from "./Profile/Profile.jsx";
import RulesManagement from "./DataQuality/RulesManagement/RulesManagement";
import Incidents from "./DataQuality/Incidents/Incidents";
import AnomalyDetection from "./AnomalyDetection/AnomalyDetection";

const OBSERVABILITY_TABS = ["profile", "rules", "incidents", "anomaly"];

function DataObservability({ assetDetail, assetObservability, initialTab = "profile", onTabChange }) {
  const [activeTab, setActiveTab] = useState(Math.max(OBSERVABILITY_TABS.indexOf(initialTab), 0));
  const [configOpen, setConfigOpen] = useState(false);
  const [configType, setConfigType] = useState("metadata_profile");
  const [jobId, setJobId] = useState(null);
  const [saving, setSaving] = useState(false);
  const [manualRunning, setManualRunning] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [formData, setFormData] = useState({
    schedule_type: "daily",
    interval_minutes: 60,
    hour: 2,
    minute: 0,
  });
  const [mlConfig, setMlConfig] = useState({
    effective_date: new Date().toISOString().slice(0, 10),
    sample_size: 10000,
    sensitivity: "medium",
  });

  const tableName = assetDetail?.table_name;
  const schemaName = assetDetail?.schema_name || "public";
  const assetName = assetDetail?.asset_name || tableName;

  const metadataPayload = useMemo(
    () => ({
      catalog: "iceberg",
      schema_name: schemaName,
      table_name: tableName,
      dag_id: "dq_metadata_collector",
      job_type: "metadata_profile",
      schedule_type: formData.schedule_type,
      interval_minutes: formData.schedule_type === "interval" ? Number(formData.interval_minutes) : null,
      hour: formData.schedule_type === "daily" ? Number(formData.hour) : null,
      minute: Number(formData.minute),
      is_active: true,
    }),
    [formData.hour, formData.interval_minutes, formData.minute, formData.schedule_type, schemaName, tableName]
  );

  useEffect(() => {
    const nextIndex = OBSERVABILITY_TABS.indexOf(initialTab);
    setActiveTab(nextIndex >= 0 ? nextIndex : 0);
  }, [initialTab]);

  useEffect(() => {
    if (!tableName) return;

    const fetchJobs = async () => {
      try {
        const response = await observabilityApi.getJobs();
        const jobs = response.data || [];
        const existingMetadataJob = jobs.find(
          (job) => job.table_name === tableName && (job.job_type || "metadata_profile") === "metadata_profile"
        );

        if (existingMetadataJob) {
          setJobId(existingMetadataJob.id);
          setFormData({
            schedule_type: existingMetadataJob.schedule_type || "daily",
            interval_minutes: existingMetadataJob.interval_minutes || 60,
            hour: existingMetadataJob.hour ?? 2,
            minute: existingMetadataJob.minute ?? 0,
          });
        } else {
          setJobId(null);
        }
      } catch (error) {
        console.error("Failed to fetch observability jobs", error);
      }
    };

    fetchJobs();
  }, [tableName]);

  const handleSaveJob = async () => {
    try {
      setSaving(true);
      if (configType === "metadata_profile") {
        if (jobId) {
          await observabilityApi.updateJob(jobId, metadataPayload);
        } else {
          const response = await observabilityApi.createJob(metadataPayload);
          setJobId(response.data?.id || null);
        }
        toast.success("Metadata profile configuration saved.");
      } else {
        toast.success("ML run configuration captured for manual execution.");
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || "Could not save the job configuration.");
    } finally {
      setSaving(false);
    }
  };

  const handleManualRun = async () => {
    try {
      setManualRunning(true);
      if (configType === "metadata_profile") {
        if (jobId) {
          await observabilityApi.triggerJob(jobId);
        } else {
          await observabilityApi.triggerScan({
            catalog: "iceberg",
            schema_name: schemaName,
            table_name: tableName,
          });
        }
        toast.success("Metadata profile run has been triggered.");
      } else {
        await observabilityApi.triggerMLScan({
          catalog: "iceberg",
          schema_name: schemaName,
          table_name: assetName,
          effective_date: mlConfig.effective_date,
          sample_size: Number(mlConfig.sample_size),
          sensitivity: mlConfig.sensitivity,
        });
        toast.success("ML anomaly run has been triggered.");
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || "Could not trigger the selected run.");
    } finally {
      setManualRunning(false);
    }
  };

  const handleDisableJob = async () => {
    if (!jobId) return;

    try {
      setDeleting(true);
      await observabilityApi.updateJob(jobId, { is_active: false });
      toast.success("Schedule disabled and Airflow DAG sync cleaned up.");
      setJobId(null);
    } catch (error) {
      toast.error(error.response?.data?.detail || "Could not disable the current job.");
    } finally {
      setDeleting(false);
    }
  };

  const handleTabChange = (_, nextTab) => {
    setActiveTab(nextTab);
    onTabChange?.(OBSERVABILITY_TABS[nextTab] || "profile");
  };

  return (
    <Box>
      <Stack
        direction={{ xs: "column", md: "row" }}
        spacing={2}
        justifyContent="space-between"
        alignItems={{ xs: "stretch", md: "center" }}
        sx={{ mb: 3 }}
      >
        <Box sx={{ borderBottom: 1, borderColor: "divider", flex: 1 }}>
          <Tabs value={activeTab} onChange={handleTabChange} variant="scrollable">
            <Tab label="Profile" />
            <Tab label="Rules" />
            <Tab label="Incidents" />
            <Tab label="Anomaly Detection" />
          </Tabs>
        </Box>

        <Button variant="outlined" startIcon={<ConfigIcon />} onClick={() => setConfigOpen(true)}>
          Configure Runs
        </Button>
      </Stack>

      {activeTab === 0 ? <Profile assetDetail={assetDetail} assetObservability={assetObservability} /> : null}
      {activeTab === 1 ? <RulesManagement assetDetail={assetDetail} /> : null}
      {activeTab === 2 ? <Incidents assetDetail={assetDetail} assetObservability={assetObservability} /> : null}
      {activeTab === 3 ? <AnomalyDetection assetDetail={assetDetail} /> : null}

      <Drawer anchor="right" open={configOpen} onClose={() => setConfigOpen(false)} PaperProps={{ sx: { width: 420, p: 3 } }}>
        <Stack spacing={3} sx={{ height: "100%" }}>
          <Box>
            <Typography variant="h5" sx={{ fontWeight: 800, mb: 0.5 }}>
              Run Configuration
            </Typography>
            <Typography color="text.secondary">
              Configure metadata collection or ML anomaly execution for <strong>{assetName}</strong>.
            </Typography>
          </Box>

          <Stack direction="row" spacing={1}>
            <Chip
              icon={<MetadataIcon />}
              label="Metadata Profile"
              color={configType === "metadata_profile" ? "primary" : "default"}
              variant={configType === "metadata_profile" ? "filled" : "outlined"}
              onClick={() => setConfigType("metadata_profile")}
            />
            <Chip
              icon={<MlIcon />}
              label="ML Run"
              color={configType === "ml" ? "primary" : "default"}
              variant={configType === "ml" ? "filled" : "outlined"}
              onClick={() => setConfigType("ml")}
            />
          </Stack>

          {configType === "metadata_profile" ? (
            <Stack spacing={2.5}>
              <Alert severity="info" sx={subtlePanelSx}>
                Metadata profile combines table-level and column-level statistics in one scheduled job.
              </Alert>

              <FormControl fullWidth>
                <InputLabel>Schedule Type</InputLabel>
                <Select
                  label="Schedule Type"
                  value={formData.schedule_type}
                  onChange={(event) =>
                    setFormData((prev) => ({
                      ...prev,
                      schedule_type: event.target.value,
                    }))
                  }
                >
                  <MenuItem value="daily">Daily at a specific time</MenuItem>
                  <MenuItem value="interval">Run every N minutes</MenuItem>
                </Select>
              </FormControl>

              {formData.schedule_type === "daily" ? (
                <Stack direction="row" spacing={2}>
                  <TextField
                    type="number"
                    label="Hour"
                    value={formData.hour}
                    onChange={(event) => setFormData((prev) => ({ ...prev, hour: event.target.value }))}
                    inputProps={{ min: 0, max: 23 }}
                    fullWidth
                  />
                  <TextField
                    type="number"
                    label="Minute"
                    value={formData.minute}
                    onChange={(event) => setFormData((prev) => ({ ...prev, minute: event.target.value }))}
                    inputProps={{ min: 0, max: 59 }}
                    fullWidth
                  />
                </Stack>
              ) : (
                <TextField
                  type="number"
                  label="Interval Minutes"
                  value={formData.interval_minutes}
                  onChange={(event) => setFormData((prev) => ({ ...prev, interval_minutes: event.target.value, minute: 0 }))}
                  inputProps={{ min: 5 }}
                  fullWidth
                />
              )}
            </Stack>
          ) : (
            <Stack spacing={2.5}>
              <Alert severity="info" sx={subtlePanelSx}>
                Pillar 4 uses unsupervised ML to detect unknown distribution shifts at scale. Choose which data date
                should be treated as "today" for the comparison run.
              </Alert>
              <TextField label="Catalog" value="iceberg" fullWidth disabled />
              <TextField label="Schema" value={schemaName} fullWidth disabled />
              <TextField label="Table" value={assetName} fullWidth disabled />
              <TextField
                type="date"
                label="Treat Data Date As Today"
                value={mlConfig.effective_date}
                onChange={(event) => setMlConfig((prev) => ({ ...prev, effective_date: event.target.value }))}
                fullWidth
                InputLabelProps={{ shrink: true }}
              />
              <TextField
                type="number"
                label="Sample Size"
                value={mlConfig.sample_size}
                onChange={(event) => setMlConfig((prev) => ({ ...prev, sample_size: event.target.value }))}
                inputProps={{ min: 1000, max: 10000, step: 500 }}
                fullWidth
              />
              <FormControl fullWidth>
                <InputLabel>Sensitivity</InputLabel>
                <Select
                  label="Sensitivity"
                  value={mlConfig.sensitivity}
                  onChange={(event) => setMlConfig((prev) => ({ ...prev, sensitivity: event.target.value }))}
                >
                  <MenuItem value="high">High sensitivity</MenuItem>
                  <MenuItem value="medium">Balanced</MenuItem>
                  <MenuItem value="low">Low sensitivity</MenuItem>
                </Select>
              </FormControl>
              <Alert severity="warning" sx={subtlePanelSx}>
                The ML engine samples data randomly, removes time-only features, and explains anomalies using feature
                importance to reduce alert fatigue.
              </Alert>
            </Stack>
          )}

          <Box sx={{ mt: "auto" }}>
            <Stack direction="row" spacing={1.5} justifyContent="flex-end">
              {configType === "metadata_profile" && jobId ? (
                <Button color="inherit" onClick={handleDisableJob} disabled={deleting}>
                  {deleting ? "Disabling..." : "Disable Schedule"}
                </Button>
              ) : null}
              {configType === "metadata_profile" ? (
                <Button variant="outlined" onClick={handleSaveJob} disabled={saving}>
                  {saving ? "Saving..." : "Save Config"}
                </Button>
              ) : null}
              <Button variant="contained" startIcon={<RunIcon />} onClick={handleManualRun} disabled={manualRunning}>
                {manualRunning ? "Starting..." : "Run Now"}
              </Button>
            </Stack>
          </Box>
        </Stack>
      </Drawer>
    </Box>
  );
}

export default DataObservability;
