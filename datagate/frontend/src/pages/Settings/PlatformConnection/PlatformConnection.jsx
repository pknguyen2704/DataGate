import React, { useState } from 'react';
import {
  Box, Button, Table, TableBody, TableCell, TableHead, TableRow,
  Paper, Typography, Stack, IconButton,
  Dialog, DialogTitle, DialogContent, DialogActions, TextField,
  Grid, Tooltip, TablePagination, TableContainer, Chip, CircularProgress
} from "@mui/material";
import {
  AddOutlined,
  VisibilityOutlined, SaveOutlined, ArrowBackOutlined
} from "@mui/icons-material";
import { useRBAC } from "~/rbac/useRBAC";
import { PermissionCode } from "~/rbac/permission";
import { connectionsApi } from "~/apis/connectionsApi";
import { StateBox, TabButton, TabContainer, StatusChip } from "~/components/Common/DataDisplay";
import { useApiResource } from "~/hooks/useApiResource";
import { toast } from "react-toastify";

import ListTable from "./ListTable/ListTable";
import Connection from "./Connection/Connection";

const INITIAL_CONNECTION = {
  connection_name: "",
  description: "",
  query_engine_host: "",
  query_engine_port: "",
  query_engine_user: "",
  query_engine_password: "",
  rest_url: "",
  catalog_name: "",
  catalog_warehouse: "",
  storage_endpoint_url: "",
  storage_access_key: "",
  storage_secret_key: "",
  is_active: true
};

function ConnectionDetailWrapper({ connectionId, onBack, onEdit, canUpdate, canDelete, canUpdateTable, canCreateTable, canDeleteTable }) {
  const [tab, setTab] = useState("config");
  const connection = useApiResource(() => connectionsApi.get(connectionId));

  if (connection.loading) return <Box sx={{ p: 10, textAlign: 'center' }}><CircularProgress /></Box>;
  if (!connection.data) return <Box sx={{ p: 5 }}>Error loading connection.</Box>;

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <IconButton onClick={onBack} sx={{ mr: 1 }} color="primary"><ArrowBackOutlined /></IconButton>
        <Typography variant="h6" fontWeight={700}>{connection.data.connection_name}</Typography>
      </Box>

      <TabContainer>
        <TabButton active={tab === "config"} onClick={() => setTab("config")} label="Configuration" />
        <TabButton active={tab === "tables"} onClick={() => setTab("tables")} label="Managed Tables" />
      </TabContainer>

      {tab === "config" && (
        <Connection
          connection={connection.data}
          canUpdate={canUpdate}
          canDelete={canDelete}
          onEdit={onEdit}
          onReload={() => connection.reload()}
          onDeleted={onBack}
        />
      )}
      {tab === "tables" && (
        <ListTable
          connectionId={connectionId}
          connectionData={connection.data}
          canUpdateTable={canUpdateTable}
          canCreateTable={canCreateTable}
          canDeleteTable={canDeleteTable}
        />
      )}
    </Box>
  );
}

export default function PlatformConnection() {
  const { hasPermission } = useRBAC();

  const canManage = hasPermission(PermissionCode.CONNECTION_MANAGE);

  const canCreate = canManage;
  const canUpdate = canManage;
  const canDelete = canManage;

  const canCreateTable = canManage;
  const canUpdateTable = canManage;
  const canDeleteTable = canManage;

  const [selectedConnectionId, setSelectedConnectionId] = useState(null);
  const [detailVersion, setDetailVersion] = useState(0);

  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);

  const connections = useApiResource(() => connectionsApi.list({
    page: page + 1,
    page_size: pageSize
  }), [page, pageSize]);

  const [openDialog, setOpenDialog] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [form, setForm] = useState(INITIAL_CONNECTION);
  const [saving, setSaving] = useState(false);

  const handleOpenAdd = () => {
    setForm(INITIAL_CONNECTION);
    setEditingId(null);
    setOpenDialog(true);
  };

  const handleOpenEdit = (row) => {
    setForm({
      ...row,
      query_engine_password: "", // Don't show old password
      storage_secret_key: "", // Don't show old secret
    });
    setEditingId(row.id);
    setOpenDialog(true);
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      if (editingId) {
        await connectionsApi.update(editingId, form);
        toast.success("Updated");
      } else {
        await connectionsApi.create(form);
        toast.success("Created");
      }
      setOpenDialog(false);
      connections.reload();
      if (selectedConnectionId) {
        setDetailVersion((prev) => prev + 1);
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || "Save failed");
    } finally {
      setSaving(false);
    }
  };

  let rows = [];
  if (connections.data && connections.data.items) {
    rows = connections.data.items;
  }

  const connectionDialog = (
    <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
      <DialogTitle sx={{ fontWeight: 'bold' }}>
        {editingId ? "Edit" : "New"} Connection
      </DialogTitle>
      <DialogContent dividers>
        <Grid container spacing={2} sx={{ mt: 0.5 }}>
          <Grid item xs={12} md={6}>
            <TextField label="Name" fullWidth size="small" value={form.connection_name} onChange={e => setForm({ ...form, connection_name: e.target.value })} />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField label="Description" fullWidth size="small" value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} />
          </Grid>

          <Grid item xs={12}><Typography variant="caption" color="primary" fontWeight={800}>QUERY ENGINE</Typography></Grid>
          <Grid item xs={12} md={4}>
            <TextField label="Host" fullWidth size="small" value={form.query_engine_host} onChange={e => setForm({ ...form, query_engine_host: e.target.value })} />
          </Grid>
          <Grid item xs={12} md={2}>
            <TextField label="Port" type="number" fullWidth size="small" value={form.query_engine_port} onChange={e => setForm({ ...form, query_engine_port: parseInt(e.target.value) })} />
          </Grid>
          <Grid item xs={12} md={3}>
            <TextField label="User" fullWidth size="small" value={form.query_engine_user} onChange={e => setForm({ ...form, query_engine_user: e.target.value })} />
          </Grid>
          <Grid item xs={12} md={3}>
            <TextField label="Password" type="password" fullWidth size="small" placeholder={editingId ? "••••••••" : ""} value={form.query_engine_password} onChange={e => setForm({ ...form, query_engine_password: e.target.value })} />
          </Grid>

          <Grid item xs={12}><Typography variant="caption" color="primary" fontWeight={800}>TABLE FORMAT</Typography></Grid>
          <Grid item xs={12} md={4}>
            <TextField label="Catalog" fullWidth size="small" value={form.catalog_name} onChange={e => setForm({ ...form, catalog_name: e.target.value })} />
          </Grid>
          <Grid item xs={12} md={4}>
            <TextField label="Rest url" fullWidth size="small" value={form.rest_url} onChange={e => setForm({ ...form, rest_url: e.target.value })} />
          </Grid>
          <Grid item xs={12} md={4}>
            <TextField label="Warehouse" fullWidth size="small" value={form.catalog_warehouse} onChange={e => setForm({ ...form, catalog_warehouse: e.target.value })} />
          </Grid>

          <Grid item xs={12}><Typography variant="caption" color="primary" fontWeight={800}>STORAGE</Typography></Grid>
          <Grid item xs={12} md={4}>
            <TextField label="Endpoint" fullWidth size="small" value={form.storage_endpoint_url} onChange={e => setForm({ ...form, storage_endpoint_url: e.target.value })} />
          </Grid>
          <Grid item xs={12} md={4}>
            <TextField label="Access Key" fullWidth size="small" value={form.storage_access_key} onChange={e => setForm({ ...form, storage_access_key: e.target.value })} />
          </Grid>
          <Grid item xs={12} md={4}>
            <TextField label="Secret Key" type="password" fullWidth size="small" placeholder={editingId ? "••••••••" : ""} value={form.storage_secret_key} onChange={e => setForm({ ...form, storage_secret_key: e.target.value })} />
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions sx={{ p: 2 }}>
        <Button onClick={() => setOpenDialog(false)} color="inherit">Cancel</Button>
        <Button variant="contained" startIcon={<SaveOutlined />} onClick={handleSave} disabled={saving}>
          {saving ? "Saving..." : "Save"}
        </Button>
      </DialogActions>
    </Dialog>
  );

  if (selectedConnectionId) {
    return (
      <>
        <ConnectionDetailWrapper
          key={`${selectedConnectionId}-${detailVersion}`}
          connectionId={selectedConnectionId}
          onBack={() => {
            setSelectedConnectionId(null);
            connections.reload();
          }}
          onEdit={handleOpenEdit}
          canUpdate={canUpdate}
          canDelete={canDelete}
          canUpdateTable={canUpdateTable}
          canCreateTable={canCreateTable}
          canDeleteTable={canDeleteTable}
        />
        {connectionDialog}
      </>
    );
  }

  return (
    <Box sx={{ p: 0 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3, alignItems: 'center' }}>
        <Box>
          <Typography variant="h5" fontWeight={800} color="primary">Platform Connections</Typography>
          <Typography variant="body2" color="text.secondary">Configure and manage connections to data sources and platforms.</Typography>
        </Box>
        <Stack direction="row" spacing={1}>
          {canCreate && (
            <Button startIcon={<AddOutlined />} variant="contained" onClick={handleOpenAdd}>
              Add Connection
            </Button>
          )}
        </Stack>
      </Box>

      <StateBox loading={connections.loading} error={connections.error} empty={!rows.length}>
        <TableContainer component={Paper} variant="outlined" sx={{ borderRadius: 2, overflow: 'hidden' }}>
          <Table size="small">
            <TableHead>
              <TableRow sx={{ bgcolor: 'primary.main' }}>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Connection Name</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Description</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Status</TableCell>
                <TableCell align="right" sx={{ color: 'white', fontWeight: 'bold' }}>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.map((row) => (
                <TableRow key={row.id} hover onClick={() => setSelectedConnectionId(row.id)} sx={{ cursor: 'pointer' }}>
                  <TableCell sx={{ fontWeight: 600 }}>{row.connection_name}</TableCell>
                  <TableCell>{row.description || "—"}</TableCell>
                  <TableCell>
                    <StatusChip value={row.is_active ? "active" : "inactive"} />
                  </TableCell>
                  <TableCell align="right">
                    <Stack direction="row" spacing={0.5} justifyContent="flex-end">
                      <Tooltip title="View Details">
                        <IconButton size="small" color="primary" onClick={() => setSelectedConnectionId(row.id)}>
                          <VisibilityOutlined fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </Stack>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          <TablePagination
            rowsPerPageOptions={[5, 10, 25]}
            component="div"
            count={connections.data?.total || 0}
            rowsPerPage={pageSize}
            page={page}
            onPageChange={(e, newPage) => setPage(newPage)}
            onRowsPerPageChange={(e) => {
              setPageSize(parseInt(e.target.value, 10));
              setPage(0);
            }}
          />
        </TableContainer>
      </StateBox>

      {connectionDialog}
    </Box>
  );
}
