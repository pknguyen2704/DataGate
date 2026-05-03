import React, { useMemo, useState } from "react";
import {
  Alert,
  CircularProgress,
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

function BoxText() {
  return (
    <Stack spacing={0.5}>
      <Typography variant="h6" fontWeight={800}>
        Data sample
      </Typography>
      <Typography color="text.secondary">
        Review live records from the selected lakehouse table.
      </Typography>
    </Stack>
  );
}

function DataSample({ assetSample, sampleStatus, sampleError, onChangeSampleLimit, sampleLimit }) {
  const sampleData = assetSample?.sample_data || assetSample || {};
  const columns = sampleData.columns || [];
  const rows = sampleData.rows || [];
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  const visibleRows = useMemo(
    () => rows.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage),
    [page, rows, rowsPerPage]
  );

  return (
    <Stack spacing={3}>
      <Paper sx={{ ...panelSx, p: 3 }}>
        <Stack
          direction={{ xs: "column", md: "row" }}
          spacing={2}
          alignItems={{ xs: "stretch", md: "center" }}
          justifyContent="space-between"
        >
          <BoxText />
          <Stack direction="row" spacing={2} alignItems="center">
            <Typography variant="body2" color="text.secondary">
              Sample size
            </Typography>
            <TextField
              select
              size="small"
              value={sampleLimit}
              onChange={(event) => {
                onChangeSampleLimit(Number(event.target.value));
                setPage(0);
              }}
              sx={{ minWidth: 120 }}
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

      {sampleError ? <Alert severity="warning">{sampleError}</Alert> : null}

      <Paper sx={{ ...panelSx, overflow: "hidden" }}>
        {sampleStatus === "loading" && !assetSample ? (
          <Stack alignItems="center" justifyContent="center" sx={{ py: 10 }}>
            <CircularProgress size={28} />
          </Stack>
        ) : (
          <>
            <TableContainer sx={{ maxHeight: 640 }}>
              <Table size="small" stickyHeader>
                <TableHead>
                  <TableRow>
                    <TableCell
                      sx={{
                        bgcolor: datagateColors.tableHeadBackground,
                        color: datagateColors.textPrimary,
                        fontWeight: 800,
                        width: 72,
                        borderBottom: `2px solid ${datagateColors.selectedBorder}`,
                      }}
                    >
                      Row
                    </TableCell>
                    {columns.map((column) => (
                      <TableCell
                        key={column}
                        sx={{
                          bgcolor: datagateColors.tableHeadBackground,
                          color: datagateColors.textPrimary,
                          fontWeight: 800,
                          minWidth: 160,
                          borderBottom: `2px solid ${datagateColors.selectedBorder}`,
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
                        <Typography color="text.secondary">
                          No sample rows available for this asset.
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ) : (
                    visibleRows.map((row, rowIndex) => (
                      <TableRow key={`${page}-${rowIndex}`} hover>
                        <TableCell sx={{ fontWeight: 700, color: "text.secondary" }}>
                          {page * rowsPerPage + rowIndex + 1}
                        </TableCell>
                        {columns.map((column, columnIndex) => {
                          const value = row?.[columnIndex];
                          return (
                            <TableCell
                              key={`${rowIndex}-${column}`}
                              sx={{
                                maxWidth: 320,
                                overflow: "hidden",
                                textOverflow: "ellipsis",
                                whiteSpace: "nowrap",
                              }}
                            >
                              {value === null || value === undefined ? (
                                <Typography component="span" sx={{ color: datagateColors.textSecondary, fontStyle: "italic" }}>
                                  NULL
                                </Typography>
                              ) : (
                                String(value)
                              )}
                            </TableCell>
                          );
                        })}
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
              onPageChange={(_, newPage) => setPage(newPage)}
              onRowsPerPageChange={(event) => {
                setRowsPerPage(parseInt(event.target.value, 10));
                setPage(0);
              }}
              sx={{ borderTop: "1px solid", borderColor: "divider" }}
            />
          </>
        )}
      </Paper>
    </Stack>
  );
}

export default DataSample;
