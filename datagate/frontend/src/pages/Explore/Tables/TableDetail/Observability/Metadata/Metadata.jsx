import React from "react";
import { Stack, Typography, Divider, Box } from "@mui/material";

import FreshnessChart from "./FreshnessChart.jsx";
import VolumeChart from "./VolumeChart.jsx";
import SchemaHistory from "./SchemaHistory.jsx";

function Metadata({ snapshots, freshnessPrediction, volumeData, volumePrediction, schemaHistory, tableName }) {
  return (
    <Stack spacing={4}>
      <Box>
        <Typography variant="h6" fontWeight={700} sx={{ mb: 1 }}>
          Data Freshness
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Track when the data was last updated and predict future delays using Prophet.
        </Typography>
        <FreshnessChart snapshots={snapshots} prediction={freshnessPrediction} />
      </Box>

      <Divider />

      <Box>
        <Typography variant="h6" fontWeight={700} sx={{ mb: 1 }}>
          Ingestion Volume
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Monitor the volume of records added over time and detect anomalies.
        </Typography>
        <VolumeChart volumeData={volumeData} prediction={volumePrediction} />
      </Box>

      <Divider />

      <Box>
        <Typography variant="h6" fontWeight={700} sx={{ mb: 1 }}>
          Schema Evolution
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Keep track of column additions, removals, and data type changes across snapshots.
        </Typography>
        <SchemaHistory schemaHistory={schemaHistory} tableName={tableName} />
      </Box>
    </Stack>
  );
}

export default Metadata;
