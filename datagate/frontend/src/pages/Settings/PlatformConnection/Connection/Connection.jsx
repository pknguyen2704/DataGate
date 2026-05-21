import React, { useState } from 'react';
import {
  Box, Button, Typography, Switch, Grid, Chip, Paper, Stack, CircularProgress
} from "@mui/material";
import { DeleteOutline, EditOutlined, BugReportOutlined } from "@mui/icons-material";
import { connectionsApi } from "~/apis/connectionsApi";
import { toast } from "react-toastify";

import { useConfirm } from "material-ui-confirm";

function Connection({ connection, canUpdate, canDelete, onEdit, onReload, onDeleted }) {
  const confirm = useConfirm();
  const [testing, setTesting] = useState(false);

  const handleTest = async () => {
    setTesting(true);
    try {
      const res = await connectionsApi.test(connection.id);
      if (res.data.success) {
        toast.success(res.data.message);
      } else {
        toast.error(res.data.message);
      }
    } catch (err) {
      toast.error("Test failed: " + (err.response?.data?.detail || err.message));
    } finally {
      setTesting(false);
    }
  };

  const handleToggleActive = async () => {
    try {
      if (connection.is_active) {
        await connectionsApi.deactivate(connection.id);
        toast.success("Deactivated");
      } else {
        await connectionsApi.activate(connection.id);
        toast.success("Activated");
      }
      onReload();
    } catch (error) {
      console.error(error);
      toast.error("Action failed");
    }
  };

  const handleDelete = () => {
    confirm({
      title: "Delete Connection",
      description: `Are you sure you want to permanently delete connection "${connection.connection_name}"?`,
      confirmationText: "Delete",
      cancellationText: "Cancel",
      confirmationButtonProps: { color: "error", variant: "contained" }
    })
      .then(async () => {
        try {
          await connectionsApi.delete(connection.id);
          toast.success("Connection deleted successfully");
          onDeleted();
        } catch (err) {
          toast.error("Failed to delete connection: " + (err.response?.data?.detail || err.message));
        }
      })
      .catch(() => { });
  };

  return (
    <Paper variant="outlined" sx={{ p: 3, borderRadius: 2 }}>
      <Grid container spacing={3}>
        <Grid item xs={12} sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 1, borderBottom: '1px solid', borderColor: 'divider', pb: 1, mb: 1 }}>
          <Typography variant="h6" color="primary" fontWeight={700}>General Info</Typography>
          <Stack direction="row" spacing={1} alignItems="center" flexWrap="wrap" useFlexGap>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Switch
                size="small"
                checked={connection.is_active}
                onChange={handleToggleActive}
                color="success"
                disabled={!canUpdate}
              />
              <Chip
                label={connection.is_active ? "Active" : "Inactive"}
                size="small"
                variant="outlined"
                color={connection.is_active ? "success" : "default"}
                sx={{ ml: 0.5, border: 'none', fontWeight: 600 }}
              />
            </Box>
            {canUpdate && (
              <Button variant="outlined" color="primary" size="small" startIcon={<EditOutlined />} onClick={() => onEdit(connection)}>
                Edit
              </Button>
            )}
            {canDelete && (
              <Button variant="outlined" color="error" size="small" startIcon={<DeleteOutline />} onClick={handleDelete}>
                Delete
              </Button>
            )}
          </Stack>
        </Grid>

        <Grid item xs={12}>
          <Typography variant="caption" color="text.secondary" fontWeight={700}>DESCRIPTION</Typography>
          <Typography variant="body2">{connection.description || "N/A"}</Typography>
        </Grid>

        <Grid item xs={12}>
          <Typography variant="h6" color="primary" fontWeight={700} sx={{ mt: 2, mb: 2, borderBottom: '1px solid', borderColor: 'divider', pb: 1 }}>Query Engine Configuration</Typography>
        </Grid>
        <Grid item xs={12} md={4}>
          <Typography variant="caption" color="text.secondary" fontWeight={700}>HOST</Typography>
          <Typography variant="body2">{connection.query_engine_host}</Typography>
        </Grid>
        <Grid item xs={12} md={4}>
          <Typography variant="caption" color="text.secondary" fontWeight={700}>PORT</Typography>
          <Typography variant="body2">{connection.query_engine_port}</Typography>
        </Grid>
        <Grid item xs={12} md={4}>
          <Typography variant="caption" color="text.secondary" fontWeight={700}>USER</Typography>
          <Typography variant="body2">{connection.query_engine_user}</Typography>
        </Grid>

        <Grid item xs={12}>
          <Typography variant="h6" color="primary" fontWeight={700} sx={{ mt: 2, mb: 2, borderBottom: '1px solid', borderColor: 'divider', pb: 1 }}>Catalog Configuration</Typography>
        </Grid>
        <Grid item xs={12} md={4}>
          <Typography variant="caption" color="text.secondary" fontWeight={700}>CATALOG NAME</Typography>
          <Typography variant="body2">{connection.catalog_name}</Typography>
        </Grid>
        <Grid item xs={12} md={4}>
          <Typography variant="caption" color="text.secondary" fontWeight={700}>REST URL</Typography>
          <Typography variant="body2">{connection.rest_url}</Typography>
        </Grid>
        <Grid item xs={12} md={4}>
          <Typography variant="caption" color="text.secondary" fontWeight={700}>WAREHOUSE</Typography>
          <Typography variant="body2" sx={{ wordBreak: 'break-all' }}>{connection.catalog_warehouse}</Typography>
        </Grid>

        <Grid item xs={12}>
          <Typography variant="h6" color="primary" fontWeight={700} sx={{ mt: 2, mb: 2, borderBottom: '1px solid', borderColor: 'divider', pb: 1 }}>Storage Configuration</Typography>
        </Grid>
        <Grid item xs={12} md={6}>
          <Typography variant="caption" color="text.secondary" fontWeight={700}>ENDPOINT URL</Typography>
          <Typography variant="body2">{connection.storage_endpoint_url}</Typography>
        </Grid>
        <Grid item xs={12} md={6}>
          <Typography variant="caption" color="text.secondary" fontWeight={700}>ACCESS KEY</Typography>
          <Typography variant="body2">{connection.storage_access_key}</Typography>
        </Grid>
      </Grid>
    </Paper>
  );
}

export default Connection;
