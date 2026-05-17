import React, { useState, useEffect, useCallback } from "react";
import { 
  Box, Button 
} from "@mui/material";
import { Launch } from "@mui/icons-material";
import { useParams } from "react-router-dom";
import { observabilityApi } from "~/apis/observabilityApi";

import { StateBox } from "~/components/Common/DataDisplay";

const Observability = () => {
  const { tableId } = useParams();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [observabilityUrl, setObservabilityUrl] = useState("");
  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      // 1. Get default time range
      const rangeRes = await observabilityApi.getDefaultTimeRange(tableId);

      // 2. Get observability URL
      const params = {};
      if (rangeRes.data?.default_from) params.from_time = rangeRes.data.default_from;
      if (rangeRes.data?.default_to) params.to_time = rangeRes.data.default_to;
      
      const res = await observabilityApi.getObservabilityUrl(tableId, params);
      setObservabilityUrl(res.data.url);
    } catch (err) {
      console.error("Failed to load observability dashboard:", err);
      setError("Could not load the observability dashboard. Please check your configuration.");
    } finally {
      setLoading(false);
    }
  }, [tableId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return (
    <StateBox 
      loading={loading} 
      error={error} 
      empty={!observabilityUrl}
      onReload={fetchData}
    >
      <Box sx={{ p: 0, height: 'calc(100vh - 350px)', minHeight: 600 }}>
        {/* Optional: Dashboard Controls Header */}
        <Box sx={{ p: 2, display: 'flex', justifyContent: 'flex-end', borderBottom: '1px solid', borderColor: 'divider' }}>
          <Button 
            size="small" 
            startIcon={<Launch />} 
            href={observabilityUrl} 
            target="_blank"
            sx={{ fontWeight: 600 }}
          >
            Open in Grafana
          </Button>
        </Box>

      {/* Embedded Dashboard */}
      <Box sx={{ width: '100%', height: '100%', position: 'relative' }}>
        <iframe
          src={observabilityUrl}
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
