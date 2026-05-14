import React from 'react';
import { Box, Typography, Paper, Alert } from "@mui/material";

const Rule = ({ detailData }) => {
  return (
    <Box>
      <Typography variant="caption" color="text.secondary" fontWeight={700}>RULE INFO</Typography>
      <Paper variant="outlined" sx={{ p: 2, mt: 1, borderRadius: 2, bgcolor: 'rgba(0,0,0,0.01)' }}>
        <Typography variant="body2" fontWeight={700}>{detailData.constraint_name}</Typography>
        <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 1 }}>{detailData.rule_description}</Typography>
        <Box sx={{ p: 1, bgcolor: '#f8f8f8', borderRadius: 1, border: '1px solid #eee' }}>
          <Typography variant="caption" component="pre" sx={{ fontSize: '0.7rem', overflow: 'auto' }}>
            {detailData.code_for_constraint}
          </Typography>
        </Box>
        {detailData.message && (
          <Alert severity="error" sx={{ mt: 2, '& .MuiAlert-message': { fontSize: '0.75rem' } }}>
            {detailData.message}
          </Alert>
        )}
      </Paper>
    </Box>
  );
};

export default Rule;