import React from 'react';
import { Box, Paper, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Chip } from '@mui/material';
import { Storage as StorageIcon } from '@mui/icons-material';

const TablePreview = ({ run }) => {
  if (!run || !run.columns) return null;

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, pt: 2 }}>
      <Paper sx={{ p: 3 }} elevation={2}>
        <Typography variant="h6" gutterBottom display="flex" alignItems="center" color="primary.main">
          <StorageIcon sx={{ mr: 1 }} /> Schema & Data Dictionary
        </Typography>
        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow sx={{ bgcolor: '#f4f6f8' }}>
                <TableCell>Column Name</TableCell>
                <TableCell>Data Type</TableCell>
                <TableCell>Distinct Values (Approx)</TableCell>
                <TableCell>Completeness</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {run.columns.map((col) => (
                <TableRow key={col.id} hover>
                  <TableCell sx={{ fontWeight: 600 }}>{col.column_name}</TableCell>
                  <TableCell>
                    <Chip label={col.data_type || 'Unknown'} size="small" variant="outlined" color="primary" />
                  </TableCell>
                  <TableCell>{col.approx_distinct_values}</TableCell>
                  <TableCell>
                    <Chip size="small" label={`${(col.completeness * 100).toFixed(1)}%`} color={col.completeness > 0.8 ? "success" : "warning"} />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
      
      <Paper sx={{ p: 3 }} elevation={2}>
        <Typography variant="h6" gutterBottom display="flex" alignItems="center" color="primary.main">
          <StorageIcon sx={{ mr: 1 }} /> Data Preview (Mock)
        </Typography>
        <Typography variant="caption" color="text.secondary" gutterBottom display="block">
          * Note: Live data previews rely on the `raw_json` response from target DB. Here is a simulated view.
        </Typography>
        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow sx={{ bgcolor: '#f4f6f8' }}>
                {run.columns.map(col => <TableCell key={col.column_name}>{col.column_name}</TableCell>)}
              </TableRow>
            </TableHead>
            <TableBody>
              {[1, 2, 3, 4, 5].map((rowIdx) => (
                <TableRow key={rowIdx} hover>
                  {run.columns.map(col => {
                    const type = (col.data_type || '').toLowerCase();
                    let mockValue = `Sample ${rowIdx}`;
                    if (type.includes('int') || type.includes('double')) mockValue = Math.floor(Math.random() * 1000);
                    if (type.includes('date')) mockValue = '2026-03-27';
                    return (
                      <TableCell key={col.column_name}>{mockValue}</TableCell>
                    )
                  })}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Box>
  );
};
export default TablePreview;