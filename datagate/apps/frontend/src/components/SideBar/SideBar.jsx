import React, { useState, useEffect } from "react";
import {
  Box,
  Typography,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  TextField,
  InputAdornment,
  Divider,
  IconButton,
  Tooltip,
  Collapse,
  Avatar
} from "@mui/material";
import {
  TableChart as TableChartIcon,
  Search as SearchIcon,
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
  ExpandMore,
  ExpandLess,
  Storage as StorageIcon,
  CloudQueue as CloudIcon,
  Layers as LayersIcon
} from "@mui/icons-material";
import { useTheme } from "@mui/material/styles";
import { useNavigate, useLocation } from "react-router-dom";
import { servicesApi } from "~/apis/services";
import TrinoIcon from "~/assets/images/Trino.svg";

const SideBar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  
  const [searchTerm, setSearchTerm] = useState("");
  const [isCollapsed, setIsCollapsed] = useState(false);
  
  const [services, setServices] = useState([]);
  const [expandedItems, setExpandedItems] = useState(["databases"]); // "databases" is open by default
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchServices = async () => {
      setLoading(true);
      try {
        const res = await servicesApi.getServices();
        setServices(res.data);
      } catch (err) {
        console.error("Failed to fetch services", err);
      } finally {
        setLoading(false);
      }
    };
    fetchServices();
  }, []);

  const toggleExpand = (id) => {
    setExpandedItems(prev => 
      prev.includes(id) ? prev.filter(item => item !== id) : [...prev, id]
    );
  };

  const getServiceIcon = (type) => {
    if (type === 'trino') return <Avatar src={TrinoIcon} sx={{ width: 18, height: 18, borderRadius: 0, '& img': { objectFit: 'contain' } }} />;
    if (type === 'postgres') return <LayersIcon sx={{ fontSize: 18, color: '#336791' }} />;
    return <StorageIcon sx={{ fontSize: 18, color: '#64748B' }} />;
  };

  const handleTableClick = (table, serviceId) => {
    navigate(`${location.pathname}?table=${table}&service=${serviceId}`);
  };

  const selectedTable = new URLSearchParams(location.search).get('table');

  return (
    <Box
      sx={{
        width: isCollapsed ? "60px" : theme.datagate.sidebarWidth,
        height: '100%',
        borderRight: `1px solid ${theme.palette.divider}`,
        bgcolor: "#FFFFFF",
        display: "flex",
        flexDirection: "column",
        overflow: "hidden",
        transition: "width 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
      }}
    >
      {/* Header */}
      <Box sx={{ p: 2, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        {!isCollapsed && (
          <Typography variant="subtitle1" sx={{ fontWeight: 800, color: "#1E293B" }}>
            Data Assets
          </Typography>
        )}
        <IconButton size="small" onClick={() => setIsCollapsed(!isCollapsed)}>
          {isCollapsed ? <ChevronRightIcon /> : <ChevronLeftIcon />}
        </IconButton>
      </Box>

      {!isCollapsed && (
        <>
          <Box sx={{ px: 2, pb: 2 }}>
            <TextField
              fullWidth
              size="small"
              placeholder="Filter assets..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon sx={{ fontSize: 18, color: "text.secondary" }} />
                  </InputAdornment>
                ),
              }}
              sx={{ "& .MuiOutlinedInput-root": { borderRadius: 2, bgcolor: "#F1F5F9", border: 'none' } }}
            />
          </Box>

          <List sx={{ flexGrow: 1, overflowY: "auto", px: 1 }}>
            {/* Root Node: Databases */}
            <ListItemButton 
              onClick={() => toggleExpand("databases")}
              sx={{ py: 0.5, borderRadius: 1 }}
            >
              <ListItemIcon sx={{ minWidth: 28 }}>
                {expandedItems.includes("databases") ? <ExpandMore fontSize="small" /> : <ChevronRightIcon fontSize="small" />}
              </ListItemIcon>
              <ListItemIcon sx={{ minWidth: 32 }}>
                <StorageIcon fontSize="small" sx={{ color: '#64748B' }} />
              </ListItemIcon>
              <ListItemText 
                primary="Databases" 
                primaryTypographyProps={{ fontSize: '0.85rem', fontWeight: 600, color: '#475569' }} 
              />
            </ListItemButton>

            <Collapse in={expandedItems.includes("databases")} timeout="auto">
              <List component="div" disablePadding sx={{ pl: 2 }}>
                {services.map((service) => (
                  <React.Fragment key={service.id}>
                    <ListItemButton 
                      onClick={() => toggleExpand(`service-${service.id}`)}
                      sx={{ py: 0.5, borderRadius: 1 }}
                    >
                      <ListItemIcon sx={{ minWidth: 28 }}>
                        {expandedItems.includes(`service-${service.id}`) ? <ExpandMore fontSize="small" /> : <ChevronRightIcon fontSize="small" />}
                      </ListItemIcon>
                      <ListItemIcon sx={{ minWidth: 32 }}>
                        {getServiceIcon(service.service_type)}
                      </ListItemIcon>
                      <ListItemText 
                        primary={service.name} 
                        primaryTypographyProps={{ fontSize: '0.85rem', fontWeight: 600, color: '#1E293B' }} 
                      />
                    </ListItemButton>

                    <Collapse in={expandedItems.includes(`service-${service.id}`)} timeout="auto">
                      <List component="div" disablePadding sx={{ pl: 4 }}>
                        {service.integrated_tables?.map((table) => (
                          <ListItemButton
                            key={`${service.id}-${table}`}
                            onClick={() => handleTableClick(table, service.id)}
                            sx={{
                              py: 0.5,
                              borderRadius: 1,
                              bgcolor: selectedTable === table ? "#E0F2FE" : "transparent",
                              color: selectedTable === table ? "#0284C7" : "#64748B",
                              "&:hover": { bgcolor: "#F1F5F9" }
                            }}
                          >
                            <ListItemIcon sx={{ minWidth: 28 }}>
                              <TableChartIcon sx={{ fontSize: 16, color: selectedTable === table ? "#0284C7" : "inherit" }} />
                            </ListItemIcon>
                            <ListItemText 
                              primary={table} 
                              primaryTypographyProps={{ fontSize: '0.8rem', fontWeight: 500, noWrap: true }} 
                            />
                          </ListItemButton>
                        ))}
                        {(!service.integrated_tables || service.integrated_tables.length === 0) && (
                          <Typography variant="caption" sx={{ pl: 4, color: 'text.disabled', fontStyle: 'italic' }}>
                            No tables integrated
                          </Typography>
                        )}
                      </List>
                    </Collapse>
                  </React.Fragment>
                ))}
              </List>
            </Collapse>
          </List>
        </>
      )}
    </Box>
  );
};

export default SideBar;
