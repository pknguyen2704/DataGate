import React, { useState } from 'react';
import {
  Box, Button, Table, TableBody, TableCell, TableHead, TableRow,
  Paper, Stack, IconButton, Switch, Chip, TableContainer,
  Dialog, DialogTitle, DialogContent, DialogActions,
  MenuItem, Select, FormControl, InputLabel
} from "@mui/material";
import { AddOutlined, DeleteOutline } from "@mui/icons-material";
import { connectionsApi } from "~/apis/connectionsApi";
import { dataAssetsApi } from "~/apis/dataAssetsApi";
import { StateBox, StatusChip } from "~/components/Common/DataDisplay";
import { useApiResource } from "~/hooks/useApiResource";
import { toast } from "react-toastify";
import { useConfirm } from "material-ui-confirm";

function ListTable({ connectionId, connectionData, canUpdateTable, canCreateTable, canDeleteTable }) {
  const confirm = useConfirm();
  const [openAdd, setOpenAdd] = useState(false);
  const [adding, setAdding] = useState(false);

  const [schemas, setSchemas] = useState([]);
  const [loadingSchemas, setLoadingSchemas] = useState(false);
  const [selectedSchema, setSelectedSchema] = useState("");

  const [discoveryTables, setDiscoveryTables] = useState([]);
  const [loadingDiscovery, setLoadingDiscovery] = useState(false);
  const [selectedTable, setSelectedTable] = useState("");

  const managedRes = useApiResource(() => dataAssetsApi.list({ connection_id: connectionId }), [connectionId]);

  const fetchSchemas = async () => {
    setLoadingSchemas(true);
    try {
      const res = await connectionsApi.discover(connectionId);
      setSchemas(res.data || []);
    } catch (error) {
      console.error(error);
      toast.error("Discovery failed");
    } finally {
      setLoadingSchemas(false);
    }
  };

  const fetchDiscoveryTables = async (schemaName) => {
    setLoadingDiscovery(true);
    try {
      const res = await connectionsApi.discover(connectionId, schemaName);
      setDiscoveryTables(res.data || []);
    } catch (error) {
      console.error(error);
      toast.error("Table discovery failed");
    } finally {
      setLoadingDiscovery(false);
    }
  };

  const handleRegister = async () => {
    setAdding(true);
    try {
      await connectionsApi.addManagedTable(connectionId, {
        catalog: connectionData.catalog_name,
        schema: selectedSchema,
        table_name: selectedTable
      });
      toast.success("Table registered");
      setOpenAdd(false);
      managedRes.reload();
    } catch (error) {
      console.error(error);
      toast.error(error.response?.data?.detail || "Registration failed");
    } finally {
      setAdding(false);
    }
  };

  const handleDelete = (tableId) => {
    confirm({
      title: "Remove Table",
      description: "Are you sure you want to remove this table from management?",
      confirmationText: "Remove",
      cancellationText: "Cancel",
      confirmationButtonProps: { color: "error", variant: "contained" }
    })
      .then(async () => {
        try {
          await connectionsApi.removeManagedTable(connectionId, tableId);
          toast.success("Removed");
          managedRes.reload();
        } catch (error) {
          console.error(error);
          toast.error("Removal failed");
        }
      })
      .catch(() => { });
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
        {canCreateTable && (
          <Button startIcon={<AddOutlined />} variant="contained" size="small" onClick={() => { setOpenAdd(true); fetchSchemas(); }}>
            Register Table
          </Button>
        )}
      </Box>

      <StateBox loading={managedRes.loading} error={managedRes.error} empty={!(managedRes.data?.items || []).length}>
        <TableContainer component={Paper} variant="outlined" sx={{ borderRadius: 2, overflow: 'hidden' }}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Schema</TableCell>
                <TableCell>Table Name</TableCell>
                <TableCell align="center">Active</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {(managedRes.data?.items || []).map((row) => (
                <TableRow key={row.id}>
                  <TableCell>{row.schema_name}</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>{row.table_name}</TableCell>
                  <TableCell align="center">
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <Switch
                        size="small"
                        checked={row.is_active}
                        color="success"
                        disabled={!canUpdateTable}
                        onChange={async (e) => {
                          const newActive = e.target.checked;
                          try {
                            await dataAssetsApi.update(row.id, { is_active: newActive });
                            toast.success(`Table ${newActive ? 'activated' : 'deactivated'}`);
                            managedRes.reload();
                          } catch (error) {
                            console.error(error);
                            toast.error("Failed to update table status");
                          }
                        }}
                      />
                      <StatusChip value={row.is_active ? "active" : "inactive"} />
                    </Box>
                  </TableCell>
                  <TableCell align="right">
                    {canDeleteTable && (
                      <IconButton size="small" color="error" onClick={() => handleDelete(row.id)}>
                        <DeleteOutline fontSize="small" />
                      </IconButton>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </StateBox>

      <Dialog open={openAdd} onClose={() => setOpenAdd(false)} maxWidth="xs" fullWidth>
        <DialogTitle sx={{ fontWeight: 700 }}>Register Managed Table</DialogTitle>
        <DialogContent dividers>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <FormControl fullWidth size="small">
              <InputLabel>Schema</InputLabel>
              <Select value={selectedSchema} label="Schema" onChange={e => { setSelectedSchema(e.target.value); fetchDiscoveryTables(e.target.value); }}>
                {loadingSchemas ? <MenuItem disabled>Loading...</MenuItem> : schemas.map(s => <MenuItem key={s} value={s}>{s}</MenuItem>)}
              </Select>
            </FormControl>
            <FormControl fullWidth size="small" disabled={!selectedSchema}>
              <InputLabel>Table</InputLabel>
              <Select value={selectedTable} label="Table" onChange={e => setSelectedTable(e.target.value)}>
                {loadingDiscovery ? <MenuItem disabled>Discovering...</MenuItem> : discoveryTables.map(t => <MenuItem key={t} value={t}>{t}</MenuItem>)}
              </Select>
            </FormControl>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenAdd(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleRegister} disabled={!selectedTable || adding}>
            {adding ? "Registering..." : "Register"}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default ListTable;
