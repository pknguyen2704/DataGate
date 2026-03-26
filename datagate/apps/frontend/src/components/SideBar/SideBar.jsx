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
} from "@mui/material";
import TableChartIcon from "@mui/icons-material/TableChart";
import SearchIcon from "@mui/icons-material/Search";
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

  const filteredTables = mockTables.filter((table) =>
    table.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <Box
      sx={{
        width: theme.datagate.sidebarWidth,
        height: `calc(100vh - ${theme.datagate.appBarHeight})`,
        borderRight: `1px solid ${theme.palette.divider}`,
        bgcolor: "background.paper",
        display: "flex",
        flexDirection: "column",
        overflow: "hidden",
      }}
    >
      <Box sx={{ p: 2 }}>
        <Typography
          variant="overline"
          sx={{
            fontWeight: 700,
            color: "text.secondary",
            letterSpacing: 1.2,
            mb: 2,
            display: "block",
            fontSize: "0.7rem",
          }}
        >
          DATAGATE TABLES
        </Typography>
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
    </Box>
  );
};

export default SideBar;
