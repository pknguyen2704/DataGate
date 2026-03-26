import React, { useState } from "react";
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
  Tooltip
} from "@mui/material";
import TableChartIcon from "@mui/icons-material/TableChart";
import SearchIcon from "@mui/icons-material/Search";
import ChevronLeftIcon from "@mui/icons-material/ChevronLeft";
import ChevronRightIcon from "@mui/icons-material/ChevronRight";
import { useTheme } from "@mui/material/styles";

const mockTables = [
  "users",
  "transactions",
  "products",
  "inventory_logs",
  "customer_profiles",
  "orders_2024",
  "payment_methods",
  "shipping_address",
  "marketing_campaigns",
  "audit_logs",
];

const SideBar = () => {
  const theme = useTheme();
  const [searchTerm, setSearchTerm] = useState("");
  const [isCollapsed, setIsCollapsed] = useState(false);

  const filteredTables = mockTables.filter((table) =>
    table.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <Box
      sx={{
        width: isCollapsed ? "60px" : theme.datagate.sidebarWidth,
        height: '100%',
        borderRight: `1px solid ${theme.palette.divider}`,
        bgcolor: "background.paper",
        display: "flex",
        flexDirection: "column",
        overflow: "hidden",
        transition: "width 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
      }}
    >
      {/* Header & Toggle Button */}
      <Box sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: isCollapsed ? 'center' : 'space-between', 
        p: 1.5,
      }}>
        {!isCollapsed && (
          <Typography
            variant="overline"
            sx={{ fontWeight: 700, color: "text.secondary", letterSpacing: 1.2, fontSize: "0.7rem", ml: 0.5 }}
          >
            DATAGATE TABLES
          </Typography>
        )}
        <Tooltip title={isCollapsed ? "Expand Sidebar" : "Collapse Sidebar"} placement="right">
          <IconButton size="small" onClick={() => setIsCollapsed(!isCollapsed)}>
            {isCollapsed ? <ChevronRightIcon fontSize="small" /> : <ChevronLeftIcon fontSize="small" />}
          </IconButton>
        </Tooltip>
      </Box>

      {!isCollapsed ? (
        <>
          <Box sx={{ px: 2, pb: 2 }}>
            <TextField
              fullWidth
              size="small"
              placeholder="Search tables..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              sx={{
                "& .MuiOutlinedInput-root": {
                  bgcolor: "#F8FAFC",
                  borderRadius: 1,
                  fontSize: "0.875rem",
                  "& fieldset": { borderColor: "divider" },
                  "&:hover fieldset": { borderColor: "primary.main" },
                  "&.Mui-focused fieldset": { borderWidth: 1 },
                },
              }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon sx={{ fontSize: 20, color: "text.secondary" }} />
                  </InputAdornment>
                ),
              }}
            />
          </Box>

          <Divider />

          <List
            sx={{
              flexGrow: 1,
              overflowY: "auto",
              px: 1,
              py: 2,
              "&::-webkit-scrollbar": { width: 6 },
              "&::-webkit-scrollbar-thumb": {
                bgcolor: "divider",
                borderRadius: 3,
              },
            }}
          >
            {filteredTables.map((table) => (
              <ListItemButton
                key={table}
                sx={{
                  borderRadius: 1,
                  mb: 0.5,
                  "&:hover": {
                    bgcolor: "rgba(30, 64, 175, 0.04)",
                    "& .MuiListItemIcon-root": { color: "primary.main" },
                    "& .MuiListItemText-primary": { color: "primary.main" },
                  },
                  transition: "all 0.2s ease",
                }}
              >
                <ListItemIcon sx={{ minWidth: 36, color: "text.secondary" }}>
                  <TableChartIcon sx={{ fontSize: 20 }} />
                </ListItemIcon>
                <ListItemText
                  primary={table}
                  primaryTypographyProps={{
                    variant: "body2",
                    fontWeight: 500,
                    noWrap: true,
                  }}
                />
              </ListItemButton>
            ))}
          </List>

          <Box sx={{ p: 2, borderTop: `1px solid ${theme.palette.divider}`, bgcolor: "rgba(0,0,0,0.02)" }}>
            <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600 }}>
              {filteredTables.length} tables managed
            </Typography>
          </Box>
        </>
      ) : (
        /* Collapsed Mode Icons */
        <List sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', pt: 1, pb: 2, flexGrow: 1 }}>
          <Divider sx={{ width: '100%', mb: 2 }} />
          {[1, 2, 3].map((item) => (
            <Tooltip key={item} title="Table Item" placement="right">
              <IconButton sx={{ mb: 1, color: "text.secondary", "&:hover": { color: "primary.main", bgcolor: "rgba(30, 64, 175, 0.04)" } }}>
                <TableChartIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          ))}
        </List>
      )}
    </Box>
  );
};

export default SideBar;
