import React, { useEffect } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Grid,
  IconButton,
  Paper,
  Stack,
  Typography,
} from '@mui/material';
import {
  Add as AddIcon,
  Block as DisableIcon,
  CheckCircle as ActiveIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Storage as StorageIcon,
  Visibility as ViewIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { useConfirm } from 'material-ui-confirm';
import { toast } from 'react-toastify';

import {
  deleteConnection,
  disableConnection,
  fetchConnections,
} from '~/stores/slices/connectionSlice';

const PlatformConnection = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const confirm = useConfirm();
  const { connections, listStatus } = useSelector((state) => state.connection);
  const loading = listStatus === 'loading';

  useEffect(() => {
    dispatch(fetchConnections());
  }, [dispatch]);

  const handleDisable = async (connection) => {
    try {
      await dispatch(disableConnection(connection.id)).unwrap();
      toast.success('Connection disabled');
    } catch (error) {
      toast.error(error || 'Disable failed');
    }
  };

  const handleDelete = async (connection) => {
    try {
      await confirm({
        title: 'Delete connection?',
        description: `Delete connection ${connection.name}?`,
        confirmationText: 'Delete',
        cancellationText: 'Cancel',
        confirmationButtonProps: {
          color: 'error',
          variant: 'contained',
        },
      });
    } catch {
      return;
    }

    try {
      await dispatch(deleteConnection(connection.id)).unwrap();
      toast.success('Connection deleted');
    } catch (error) {
      toast.error(error || 'Delete failed');
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 2, mb: 4 }}>
        <Box>
          <Typography variant="h4" fontWeight={900}>Platform Connections</Typography>
          <Typography variant="body2" color="text.secondary">
            Manage lakehouse platforms and the tables registered under each platform.
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => navigate('/settings/connection/new')}
          sx={{ borderRadius: '8px', fontWeight: 700, whiteSpace: 'nowrap' }}
        >
          Add Connection
        </Button>
      </Box>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 10 }}>
          <CircularProgress />
        </Box>
      ) : connections.length === 0 ? (
        <Paper
          elevation={0}
          sx={{
            p: 8,
            textAlign: 'center',
            border: '1px dashed',
            borderColor: 'divider',
            bgcolor: 'background.paper',
            borderRadius: '8px',
          }}
        >
          <StorageIcon sx={{ fontSize: 56, color: 'text.disabled', mb: 2 }} />
          <Typography variant="h6" fontWeight={800}>No platforms connected</Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5, mb: 3 }}>
            Add a platform connection before registering managed tables.
          </Typography>
          <Button variant="outlined" startIcon={<AddIcon />} onClick={() => navigate('/settings/connection/new')}>
            Add Connection
          </Button>
        </Paper>
      ) : (
        <Grid container spacing={2.5}>
          {connections.map((connection) => (
            <Grid item xs={12} md={6} xl={4} key={connection.id}>
              <Card
                elevation={0}
                sx={{
                  height: '100%',
                  border: '1px solid',
                  borderColor: 'divider',
                  borderRadius: '8px',
                  bgcolor: 'background.paper',
                }}
              >
                <CardContent sx={{ p: 3 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', gap: 2 }}>
                    <Box sx={{ display: 'flex', gap: 1.5, minWidth: 0 }}>
                      <Box
                        sx={{
                          width: 44,
                          height: 44,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          borderRadius: '8px',
                          bgcolor: 'primary.50',
                          color: 'primary.main',
                          flexShrink: 0,
                        }}
                      >
                        <StorageIcon />
                      </Box>
                      <Box sx={{ minWidth: 0 }}>
                        <Typography variant="subtitle1" fontWeight={800} noWrap>{connection.name}</Typography>
                        <Typography variant="body2" color="text.secondary" noWrap>
                          {connection.description || 'No description'}
                        </Typography>
                      </Box>
                    </Box>
                    <Chip
                      icon={connection.is_active ? <ActiveIcon fontSize="small" /> : undefined}
                      label={connection.is_active ? 'Active' : 'Disabled'}
                      color={connection.is_active ? 'success' : 'default'}
                      size="small"
                      variant="outlined"
                      sx={{ fontWeight: 700 }}
                    />
                  </Box>

                  <Stack direction="row" spacing={1} sx={{ mt: 2, flexWrap: 'wrap', rowGap: 1 }}>
                    <Chip label={`Trino ${connection.trino_host}:${connection.trino_port}`} size="small" />
                    <Chip label={connection.iceberg_catalog_name} size="small" variant="outlined" />
                  </Stack>

                  <Stack direction="row" spacing={1} sx={{ mt: 3 }}>
                    <Button
                      size="small"
                      variant="contained"
                      startIcon={<ViewIcon />}
                      onClick={() => navigate(`/settings/connection/${connection.id}`)}
                    >
                      Manage
                    </Button>
                    <IconButton size="small" onClick={() => navigate(`/settings/connection/${connection.id}`)}>
                      <EditIcon fontSize="small" />
                    </IconButton>
                    <IconButton
                      size="small"
                      disabled={!connection.is_active}
                      onClick={() => handleDisable(connection)}
                    >
                      <DisableIcon fontSize="small" />
                    </IconButton>
                    <IconButton size="small" color="error" onClick={() => handleDelete(connection)}>
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );
};

export default PlatformConnection;
