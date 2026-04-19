import React, { useMemo, useState } from "react";
import {
  Box,
  Chip,
  InputAdornment,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";
import {
  DescriptionOutlined as DescriptionIcon,
  Search as SearchIcon,
  SchemaOutlined as SchemaIcon,
  TableChartOutlined as TableIcon,
} from "@mui/icons-material";
import { datagateColors, panelSx, subtlePanelSx } from "~/theme";

const formatValue = (value) => {
  if (value === null || value === undefined || value === "") return "--";
  if (typeof value === "number") return value.toLocaleString();
  return value;
};

const getColumnDescription = (column) =>
  column?.description ||
  column?.column_description ||
  column?.comment ||
  column?.column_comment ||
  "--";

function Overview({ assetDetail, assetObservability }) {
  const [query, setQuery] = useState("");

  const columns = useMemo(() => {
    if (Array.isArray(assetDetail?.columns) && assetDetail.columns.length > 0) {
      return assetDetail.columns;
    }
    return assetObservability?.schema || [];
  }, [assetDetail?.columns, assetObservability?.schema]);

  const normalizedQuery = query.trim().toLowerCase();

  const filteredColumns = useMemo(() => {
    if (!normalizedQuery) return columns;

    return columns.filter((column) => {
      const haystack = [
        column?.column_name,
        column?.data_type,
        getColumnDescription(column),
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();

      return haystack.includes(normalizedQuery);
    });
  }, [columns, normalizedQuery]);

  return (
    <Stack spacing={2.5}>
      <Paper sx={{ ...panelSx, overflow: "hidden", borderRadius: 1 }}>
        <Stack
          direction={{ xs: "column", md: "row" }}
          spacing={2}
          justifyContent="space-between"
          alignItems={{ xs: "stretch", md: "center" }}
          sx={{ p: 2, borderBottom: "1px solid #f1f5f9" }}
        >
          <TextField
            size="small"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search columns..."
            fullWidth
            sx={{ maxWidth: 400 }}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon fontSize="small" />
                </InputAdornment>
              ),
              sx: { borderRadius: 1, bgcolor: "#f8fafc" }
            }}
          />

          <Chip
            icon={<TableIcon sx={{ fontSize: 16 }} />}
            label={`${columns.length} Fields`}
            size="small"
            variant="outlined"
            sx={{ borderRadius: 1, fontWeight: 600 }}
          />
        </Stack>

        <TableContainer>
          <Table size="small">
            <TableHead sx={{ backgroundColor: "#f8fafc" }}>
              <TableRow>
                <TableCell sx={{ fontWeight: 700, color: "text.primary", py: 1.5 }}>Field Name</TableCell>
                <TableCell sx={{ fontWeight: 700, color: "text.primary", py: 1.5 }}>Data Type</TableCell>
                <TableCell sx={{ fontWeight: 700, color: "text.primary", py: 1.5 }}>Description</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredColumns.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={3} align="center" sx={{ py: 6 }}>
                    <Typography variant="body2" color="text.secondary">
                      {columns.length === 0
                        ? "No metadata found for this table."
                        : "No matching fields found."}
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                filteredColumns.map((column, index) => (
                  <TableRow
                    key={`${column.column_name}-${index}`}
                    hover
                    sx={{ "& td": { borderBottom: "1px solid #f8fafc" } }}
                  >
                    <TableCell sx={{ fontWeight: 600, color: "primary.main", width: "30%" }}>
                      {formatValue(column.column_name)}
                    </TableCell>
                    <TableCell sx={{ width: "20%" }}>
                      <Typography variant="caption" sx={{ 
                        fontFamily: "monospace", 
                        bgcolor: "#f1f5f9", 
                        px: 1, 
                        py: 0.5, 
                        borderRadius: 0.5,
                        color: "#475569"
                      }}>
                        {formatValue(column.data_type)}
                      </Typography>
                    </TableCell>
                    <TableCell sx={{ color: "text.secondary", fontSize: "0.875rem" }}>
                      {getColumnDescription(column)}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Stack>
  );
}

export default Overview;
