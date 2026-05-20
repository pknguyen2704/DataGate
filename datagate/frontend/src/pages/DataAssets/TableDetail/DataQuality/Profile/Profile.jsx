import React from 'react';
import { Box, Typography, Paper, Stack } from "@mui/material";

const Profile = ({ detailData }) => {
  return (
    <Box>
      <Typography variant="caption" color="text.secondary" fontWeight={700}>THRESHOLD INFO</Typography>
      <Paper variant="outlined" sx={{ p: 2, mt: 1, borderRadius: 2, bgcolor: 'rgba(0,0,0,0.01)' }}>
        <Stack spacing={1}>
          <Stack direction="row" justifyContent="space-between">
            <Typography variant="body2">Metric Name</Typography>
            <Typography variant="body2" fontWeight={600}>{detailData.metric_name}</Typography>
          </Stack>
          <Stack direction="row" justifyContent="space-between">
            <Typography variant="body2">Actual Value</Typography>
            <Typography variant="body2" fontWeight={600}>{detailData.actual_value?.toFixed(4)}</Typography>
          </Stack>
          <Stack direction="row" justifyContent="space-between">
            <Typography variant="body2">Min Threshold</Typography>
            <Typography variant="body2">{detailData.min_threshold ?? 'N/A'}</Typography>
          </Stack>
          <Stack direction="row" justifyContent="space-between">
            <Typography variant="body2">Max Threshold</Typography>
            <Typography variant="body2">{detailData.max_threshold ?? 'N/A'}</Typography>
          </Stack>
        </Stack>
      </Paper>
      {detailData.description && (
        <Paper variant="outlined" sx={{ p: 2, mt: 2, borderRadius: 2, bgcolor: 'rgba(0,0,0,0.01)' }}>
          <Typography variant="caption" color="text.secondary" fontWeight={700}>DESCRIPTION</Typography>
          <Typography variant="body2" sx={{ mt: 1 }}>{detailData.description}</Typography>
        </Paper>
      )}
    </Box>
  );
};

export default Profile;