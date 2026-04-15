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

function TableDescription({ assetDetail, assetObservability }) {
  const [query, setQuery] = useState("");

  const columns = useMemo(() => {
    if (Array.isArray(assetDetail?.columns) && assetDetail.columns.length > 0) {
      return assetDetail.columns;
    }
    return assetObservability?.schema || [];
  }, [assetDetail?.columns, assetObservability?.schema]);
  const normalizedQuery = query.trim().toLowerCase();
  const tableDescription = assetDetail?.table_description || `Metadata for ${formatValue(assetDetail?.asset_name)}.`;

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
    <Stack spacing={3}>
      <Paper
        sx={{
          p: 3,
          borderRadius: 4,
          border: "1px solid",
          borderColor: "divider",
          boxShadow: "none",
        }}
      >
        <Stack spacing={2.5}>
          <Stack direction="row" alignItems="center" spacing={1.5}>
            <DescriptionIcon color="primary" />
            <Typography variant="h6" fontWeight={800}>
              Description
            </Typography>
          </Stack>

          <Box
            sx={{
              p: 3,
              minHeight: 160,
              borderRadius: 3,
              border: "1px solid",
              borderColor: "#D9E1EC",
              backgroundColor: "#FCFDFE",
            }}
          >
            <Stack spacing={2}>
              <Stack direction="row" spacing={1} alignItems="center">
                <SchemaIcon sx={{ color: "text.secondary" }} fontSize="small" />
                <Typography fontWeight={700}>{formatValue(assetDetail?.asset_name)}</Typography>
              </Stack>
              <Typography variant="body1" color="text.secondary">
                Schema: {formatValue(assetDetail?.schema_name)}
              </Typography>
              <Typography variant="body1" sx={{ color: "text.primary" }}>
                {tableDescription}
              </Typography>
              <Typography variant="body2" sx={{ color: "text.secondary" }}>
                This table currently exposes {formatValue(columns.length)} columns from synchronized source metadata.
              </Typography>
            </Stack>
          </Box>
        </Stack>
      </Paper>

      <Paper
        sx={{
          overflow: "hidden",
          borderRadius: 4,
          border: "1px solid",
          borderColor: "divider",
          boxShadow: "none",
        }}
      >
        <Stack
          direction={{ xs: "column", md: "row" }}
          spacing={2}
          justifyContent="space-between"
          alignItems={{ xs: "stretch", md: "center" }}
          sx={{ p: 3 }}
        >
          <TextField
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Find in table"
            fullWidth
            sx={{ maxWidth: 560 }}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
          />

          <Stack direction="row" spacing={1} alignItems="center">
            <Chip
              icon={<TableIcon />}
              label={`${filteredColumns.length} / ${columns.length} columns`}
              variant="outlined"
              sx={{ px: 1, height: 36 }}
            />
          </Stack>
        </Stack>

        <TableContainer>
          <Table>
            <TableHead sx={{ backgroundColor: "#F8FAFC" }}>
              <TableRow>
                <TableCell sx={{ fontWeight: 800, color: "primary.main" }}>Name</TableCell>
                <TableCell sx={{ fontWeight: 800 }}>Type</TableCell>
                <TableCell sx={{ fontWeight: 800 }}>Description</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredColumns.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={3} align="center" sx={{ py: 8 }}>
                    <Typography color="text.secondary">
                      {columns.length === 0
                        ? "No schema metadata is available for this table."
                        : "No matching columns were found."}
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                filteredColumns.map((column, index) => (
                  <TableRow
                    key={`${column.column_name}-${index}`}
                    hover
                    sx={{
                      "& td": {
                        py: 2.5,
                        verticalAlign: "top",
                      },
                    }}
                  >
                    <TableCell sx={{ fontWeight: 700, color: "primary.main", minWidth: 220 }}>
                      {formatValue(column.column_name)}
                    </TableCell>
                    <TableCell sx={{ minWidth: 180 }}>
                      <Chip
                        size="small"
                        label={formatValue(column.data_type)}
                        variant="outlined"
                        sx={{ borderRadius: 2 }}
                      />
                    </TableCell>
                    <TableCell sx={{ color: "text.secondary" }}>
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

export default TableDescription;
