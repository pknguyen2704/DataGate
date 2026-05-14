import React, { useState, useEffect } from "react";
import { 
  Box, Button, Stack, Skeleton, Alert 
} from "@mui/material";
import { Refresh, Launch } from "@mui/icons-material";
import { useParams } from "react-router-dom";
import { observabilityApi } from "~/apis/observabilityApi";

import { StateBox } from "~/components/DataGate/Page";

const Observability = () => {
  const { tableId } = useParams();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dashboardUrl, setDashboardUrl] = useState("");
  const [timeRange, setTimeRange] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      // 1. Get default time range
      const rangeRes = await observabilityApi.getDefaultTimeRange(tableId);
      setTimeRange(rangeRes.data);

      // 2. Get dashboard URL
      const params = {};
      if (rangeRes.data?.default_from) params.from_time = rangeRes.data.default_from;
      if (rangeRes.data?.default_to) params.to_time = rangeRes.data.default_to;
      
      const dashboardRes = await observabilityApi.getDashboardUrl(tableId, params);
      setDashboardUrl(dashboardRes.data.url);
    } catch (err) {
      console.error("Failed to load observability dashboard:", err);
      setError("Could not load the observability dashboard. Please check your Grafana configuration.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [tableId]);

  return (
    <StateBox 
      loading={loading} 
      error={error} 
      empty={!dashboardUrl}
      onReload={fetchData}
    >
      <Box sx={{ p: 0, height: 'calc(100vh - 350px)', minHeight: 600 }}>
        {/* Optional: Dashboard Controls Header */}
        <Box sx={{ p: 2, display: 'flex', justifyContent: 'flex-end', borderBottom: '1px solid', borderColor: 'divider' }}>
          <Button 
            size="small" 
            startIcon={<Launch />} 
            href={dashboardUrl} 
            target="_blank"
            sx={{ fontWeight: 600 }}
          >
            Open in Grafana
          </Button>
        </Box>

      {/* Embedded Dashboard */}
      <Box sx={{ width: '100%', height: '100%', position: 'relative' }}>
        <iframe
          src={dashboardUrl}
          width="100%"
          height="100%"
          frameBorder="0"
          style={{ border: 0 }}
          title="Data Observability Dashboard"
          allowFullScreen
        />
      </Box>
    </Box>
  </StateBox>
  );
};

export default Observability;