import React from "react";
import {
  Box,
  Typography,
  Paper,
  IconButton,
  Tooltip,
  useTheme,
} from "@mui/material";
import {
  FilterAlt as FilterIcon,
  ZoomIn,
  ZoomOut,
  CenterFocusStrong,
  Storage,
  Layers,
  Diamond,
  Dashboard,
} from "@mui/icons-material";

const LineageNode = ({ name, type, status, x, y }) => {
  const icons = {
    source: <Storage color="inherit" />,
    bronze: <Layers color="inherit" />,
    silver: <Diamond color="inherit" />,
    gold: <Dashboard color="inherit" />,
    dashboard: <Box sx={{ width: 16, height: 16, border: '2px solid' }} />,
  };

  const colors = {
    healthy: '#10B981',
    warning: '#F59E0B',
    error: '#EF4444',
  };

  return (
    <Box
      sx={{
        position: 'absolute',
        left: x,
        top: y,
        transform: 'translate(-50%, -50%)',
        zIndex: 2,
      }}
    >
      <Paper
        className="glass-card"
        sx={{
          p: 1.5,
          width: 140,
          textAlign: 'center',
          borderRadius: '12px',
          border: '2px solid',
          borderColor: colors[status] || '#E2E8F0',
          cursor: 'pointer',
          transition: 'all 0.2s',
          '&:hover': { transform: 'scale(1.05)', boxShadow: '0 8px 16px rgba(0,0,0,0.1)' }
        }}
      >
        <Box sx={{ color: colors[status] || 'primary.main', mb: 0.5 }}>{icons[type]}</Box>
        <Typography variant="caption" sx={{ fontWeight: 800, display: 'block' }}>{name}</Typography>
        <Typography variant="caption" color="text.secondary" sx={{ fontSize: '9px', textTransform: 'uppercase' }}>{type}</Typography>
      </Paper>
    </Box>
  );
};

const DataLineage = () => {
  const theme = useTheme();

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 800 }}>Data Lineage</Typography>
          <Typography variant="body1" color="text.secondary">Trace data flow from raw sources to final dashboards.</Typography>
        </Box>
        <Paper sx={{ p: 0.5, borderRadius: '8px', display: 'flex', gap: 0.5 }}>
           <IconButton size="small"><ZoomIn /></IconButton>
           <IconButton size="small"><ZoomOut /></IconButton>
           <IconButton size="small"><CenterFocusStrong /></IconButton>
           <IconButton size="small"><FilterIcon /></IconButton>
        </Paper>
      </Box>

      <Paper 
        sx={{ 
          flexGrow: 1, 
          bgcolor: '#F1F5F9', 
          position: 'relative', 
          overflow: 'hidden',
          backgroundImage: 'radial-gradient(#E2E8F0 1px, transparent 1px)',
          backgroundSize: '24px 24px'
        }}
      >
        <svg 
           style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', pointerEvents: 'none' }}
        >
          {/* Mock Connection Lines */}
          <path d="M 120,300 C 250,300 250,200 380,200" stroke="#CBD5E1" strokeWidth="2" fill="none" />
          <path d="M 120,300 C 250,300 250,400 380,400" stroke="#CBD5E1" strokeWidth="2" fill="none" />
          <path d="M 380,200 C 500,200 500,300 640,300" stroke="#CBD5E1" strokeWidth="2" fill="none" />
          <path d="M 380,400 C 500,400 500,300 640,300" stroke="#CBD5E1" strokeWidth="2" fill="none" />
          <path d="M 640,300 C 780,300 780,300 900,300" stroke="#CBD5E1" strokeWidth="3" fill="none" />
          <path d="M 900,300 C 1050,300 1050,300 1200,300" stroke="#3B82F6" strokeWidth="4" fill="none" strokeDasharray="8 4" />
        </svg>

        <LineageNode name="Postgres_S3" type="source" status="healthy" x={120} y={300} />
        
        <LineageNode name="bronze_trips" type="bronze" status="healthy" x={380} y={200} />
        <LineageNode name="bronze_zones" type="bronze" status="healthy" x={380} y={400} />
        
        <LineageNode name="silver_clean_trips" type="silver" status="warning" x={640} y={300} />
        
        <LineageNode name="gold_agg_trips" type="gold" status="healthy" x={900} y={300} />
        
        <LineageNode name="Executive_Dashboard" type="dashboard" status="healthy" x={1200} y={300} />

        <Box sx={{ position: 'absolute', bottom: 24, left: 24 }}>
           <Paper sx={{ p: 2, borderRadius: '12px' }}>
              <Typography variant="caption" fontWeight={700} display="block" gutterBottom>Legend</Typography>
              <Stack spacing={1}>
                 <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Box sx={{ width: 10, height: 10, borderRadius: '50%', bgcolor: '#10B981' }} />
                    <Typography variant="caption">Healthy</Typography>
                 </Box>
                 <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Box sx={{ width: 10, height: 10, borderRadius: '50%', bgcolor: '#F59E0B' }} />
                    <Typography variant="caption">Delayed / Warning</Typography>
                 </Box>
                 <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Box sx={{ width: 10, height: 10, borderRadius: '50%', bgcolor: '#EF4444' }} />
                    <Typography variant="caption">Critical Issue</Typography>
                 </Box>
              </Stack>
           </Paper>
        </Box>
      </Paper>
    </Box>
  );
};

export default DataLineage;
