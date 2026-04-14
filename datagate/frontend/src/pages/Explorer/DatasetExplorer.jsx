import React, { useState } from "react";
import {
  Box,
  Typography,
  Paper,
  Grid,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tabs,
  Tab,
  TextField,
  InputAdornment,
  Button,
} from "@mui/material";
import {
  Search as SearchIcon,
  FilterList as FilterIcon,
  FileDownload as DownloadIcon,
  Analytics as ProfilingIcon,
  TableRows as RowsIcon,
} from "@mui/icons-material";

const DatasetExplorer = () => {
  const [activeTab, setActiveTab] = useState(0);

  return (
    <Box>
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 800 }}>Dataset Explorer</Typography>
          <Typography variant="body1" color="text.secondary">Preview raw records, inspect schemas, and view automatic profiling stats.</Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 2 }}>
           <TextField 
             size="small" 
             placeholder="Search within dataset..." 
             InputProps={{ startAdornment: <InputAdornment position="start"><SearchIcon fontSize="small" /></InputAdornment> }}
             sx={{ bgcolor: 'white' }}
           />
           <Button variant="outlined" startIcon={<FilterIcon />}>Filters</Button>
           <Button variant="contained" startIcon={<DownloadIcon />}>Export CSV</Button>
        </Box>
      </Box>

      <Paper sx={{ mb: 4 }}>
        <Tabs value={activeTab} onChange={(e, v) => setActiveTab(v)} sx={{ px: 2, borderBottom: 1, borderColor: 'divider' }}>
          <Tab label="Data Preview" icon={<RowsIcon fontSize="small" />} iconPosition="start" />
          <Tab label="Profiling Stats" icon={<ProfilingIcon fontSize="small" />} iconPosition="start" />
        </Tabs>

        <Box sx={{ p: 3 }}>
          {activeTab === 0 ? (
            <TableContainer sx={{ border: '1px solid #E2E8F0', borderRadius: '8px' }}>
              <Table size="small">
                <TableHead sx={{ bgcolor: '#F8FAFC' }}>
                  <TableRow>
                    {['vendor_id', 'tpep_pickup_datetime', 'trip_distance', 'fare_amount', 'total_amount', 'improvement_surcharge'].map(h => (
                      <TableCell key={h} sx={{ fontWeight: 700, fontSize: '11px', whiteSpace: 'nowrap' }}>{h.toUpperCase()}</TableCell>
                    ))}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {[
                    [1, '2025-10-14 09:12:00', 1.2, 12.5, 15.0, 0.3],
                    [2, '2025-10-14 09:15:22', 4.5, 24.0, 28.5, 0.3],
                    [1, '2025-10-14 09:20:05', 0.8, 8.5, 10.2, 0.3],
                    [1, '2025-10-14 09:32:00', 3.2, 18.5, 22.0, 0.3],
                    [2, '2025-10-14 09:45:00', 10.4, 45.0, 52.3, 0.3],
                  ].map((row, i) => (
                    <TableRow key={i} hover>
                      {row.map((cell, j) => (
                        <TableCell key={j} sx={{ fontSize: '12px' }}>{cell}</TableCell>
                      ))}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          ) : (
            <Grid container spacing={3}>
               {[
                 { col: 'vendor_id', dist: '1: 42%, 2: 58%', card: 2, nulls: 0 },
                 { col: 'trip_distance', min: 0, max: 84.2, mean: 2.8, std: 1.4 },
                 { col: 'fare_amount', min: -5.0, max: 200.0, mean: 14.2, anomalies: 4 },
                 { col: 'payment_type', dist: 'Cash: 12%, Card: 88%', card: 2, nulls: 0 },
               ].map((stat, i) => (
                 <Grid item xs={12} md={6} key={i}>
                    <Paper variant="outlined" sx={{ p: 2, borderRadius: '12px' }}>
                       <Typography variant="subtitle2" fontWeight={800} gutterBottom>{stat.col}</Typography>
                       <Grid container spacing={1}>
                          {Object.entries(stat).filter(([k]) => k !== 'col').map(([k, v]) => (
                             <Grid item xs={6} key={k}>
                                <Typography variant="caption" color="text.secondary" display="block">{k.toUpperCase()}</Typography>
                                <Typography variant="body2" fontWeight={600}>{v}</Typography>
                             </Grid>
                          ))}
                       </Grid>
                    </Paper>
                 </Grid>
               ))}
            </Grid>
          )}
        </Box>
      </Paper>
    </Box>
  );
};

export default DatasetExplorer;
