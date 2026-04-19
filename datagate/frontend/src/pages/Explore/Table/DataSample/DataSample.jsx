import React, { useState } from "react";
import {
  MenuItem,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TablePagination,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";
import { datagateColors, panelSx } from "~/theme";

function DataSample({ assetSample, onChangeSampleLimit, sampleLimit }) {
  const sampleData = assetSample?.sample_data || {};
  const columns = sampleData?.columns || [];
  const rows = sampleData?.rows || [];

  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  // Tính toán dữ liệu hiển thị cho trang hiện tại
  const visibleRows = rows.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage);

  return (
    <Stack spacing={3}>
      <Paper sx={{ p: 3, borderRadius: 2, boxShadow: "0 2px 10px rgba(0,0,0,0.05)" }}>
        <Stack direction={{ xs: "column", md: "row" }} spacing={2} alignItems="center" justifyContent="space-between">
          <BoxText />
          <Stack direction="row" spacing={2} alignItems="center">
            <Typography variant="body2" color="text.secondary">Fetch limit:</Typography>
            <TextField
              select
              size="small"
              value={sampleLimit}
              onChange={(event) => {
                onChangeSampleLimit(Number(event.target.value));
                setPage(0); // Reset page when limit changes
              }}
              sx={{ minWidth: 100 }}
            >
              {[10, 25, 50, 100, 200, 500].map((value) => (
                <MenuItem key={value} value={value}>
                  {value}
                </MenuItem>
              ))}
            </TextField>
          </Stack>
        </Stack>
      </Paper>

      <Paper sx={{ ...panelSx, overflow: "hidden", borderRadius: 2, boxShadow: "0 4px 20px rgba(0,0,0,0.08)" }}>
        <TableContainer sx={{ maxHeight: 600 }}>
          <Table size="small" stickyHeader>
            <TableHead>
              <TableRow>
                {/* Cột số thứ tự nổi bật */}
                <TableCell 
                  sx={{ 
                    bgcolor: "#f8f9fa", 
                    fontWeight: 800, 
                    color: datagateColors.primary,
                    width: 60,
                    borderBottom: `2px solid ${datagateColors.primary}`,
                    zIndex: 10
                  }}
                >
                  No.
                </TableCell>
                {columns.map((column) => (
                  <TableCell 
                    key={column} 
                    sx={{ 
                      bgcolor: "#f8f9fa",
                      fontWeight: 800,
                      whiteSpace: "nowrap",
                      borderBottom: `2px solid ${datagateColors.primary}`,
                      minWidth: 150
                    }}
                  >
                    {column}
                  </TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={columns.length + 1} align="center" sx={{ py: 10 }}>
                    <Typography color="text.secondary" variant="body1">
                      No sample rows available for this asset.
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                visibleRows.map((row, rowIndex) => (
                  <TableRow key={rowIndex} hover sx={{ '&:nth-of-type(even)': { bgcolor: '#fafafa' } }}>
                    <TableCell sx={{ fontWeight: 600, color: "text.secondary", borderRight: "1px solid #eee" }}>
                      {page * rowsPerPage + rowIndex + 1}
                    </TableCell>
                    {columns.map((column, columnIndex) => (
                      <TableCell 
                        key={`${rowIndex}-${column}`}
                        sx={{ 
                          maxWidth: 300, 
                          overflow: "hidden", 
                          textOverflow: "ellipsis", 
                          whiteSpace: "nowrap" 
                        }}
                      >
                        {row?.[columnIndex] === null || row?.[columnIndex] === undefined 
                          ? <Typography component="span" sx={{ color: "#ccc", fontStyle: "italic", fontSize: "0.8rem" }}>NULL</Typography>
                          : String(row[columnIndex])
                        }
                      </TableCell>
                    ))}
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          rowsPerPageOptions={[10, 25, 50]}
          component="div"
          count={rows.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
          sx={{ borderTop: "1px solid #eee" }}
        />
      </Paper>
    </Stack>
  );
}

function BoxText() {
  return (
    <Stack spacing={0.5}>
      <Typography variant="h6" fontWeight={700}>
        Data Sample
      </Typography>
      <Typography color="text.secondary">
        Review raw records returned from the selected asset.
      </Typography>
    </Stack>
  );
}

export default DataSample;
