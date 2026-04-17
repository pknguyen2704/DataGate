import React from "react";
import {
  MenuItem,
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
import { datagateColors, panelSx } from "~/theme";

function DataSample({ assetDetail, onChangeSampleLimit, sampleLimit }) {
  const sampleData = assetDetail?.sample_data || {};
  const columns = sampleData?.columns || [];
  const rows = sampleData?.rows || [];

  return (
    <Stack spacing={3}>
      <Paper sx={{ p: 3 }}>
        <Stack direction={{ xs: "column", md: "row" }} spacing={2} justifyContent="space-between">
          <BoxText />
          <TextField
            select
            label="Rows"
            value={sampleLimit}
            onChange={(event) => onChangeSampleLimit(Number(event.target.value))}
            sx={{ minWidth: 120 }}
          >
            {[10, 25, 50, 100].map((value) => (
              <MenuItem key={value} value={value}>
                {value}
              </MenuItem>
            ))}
          </TextField>
        </Stack>
      </Paper>

      <Paper sx={{ ...panelSx, overflow: "hidden" }}>
        <TableContainer>
          <Table size="small">
            <TableHead sx={{ bgcolor: datagateColors.tableHeadBackground }}>
              <TableRow>
                {columns.map((column) => (
                  <TableCell key={column} sx={{ fontWeight: 700 }}>
                    {column}
                  </TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={Math.max(columns.length, 1)} align="center" sx={{ py: 6 }}>
                    <Typography color="text.secondary">No sample rows available.</Typography>
                  </TableCell>
                </TableRow>
              ) : (
                rows.map((row, rowIndex) => (
                  <TableRow key={rowIndex} hover>
                    {columns.map((column, columnIndex) => (
                      <TableCell key={`${rowIndex}-${column}`}>
                        {String(row?.[columnIndex] ?? "--")}
                      </TableCell>
                    ))}
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
