import React, { useEffect, useState } from "react";
import { Alert, Box, Button, Skeleton, Typography, Breadcrumbs, Link, Stack, Paper } from "@mui/material";
import { 
  OpenInNewOutlined as OpenInNewIcon, 
  Refresh as RefreshIcon,
  MenuBookOutlined as NotebookIcon
} from "@mui/icons-material";
import { Link as RouterLink } from "react-router-dom";
import { labApi } from "~/apis/labApi";

function Notebook() {
  const [notebookUrl, setNotebookUrl] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchNotebookUrl = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await labApi.getNotebookUrl();
      setNotebookUrl(res.data.url);
    } catch (err) {
      console.error("Failed to load notebook:", err);
      setError("Could not load the notebook. Please check your Jupyter configuration.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNotebookUrl();
  }, []);

  return (
    <Box
      sx={{
        p: { xs: 2, md: 3 },
        bgcolor: "background.default",
        flexGrow: 1,
        display: "flex",
        flexDirection: "column",
        minHeight: 0,
      }}
    >
      <Breadcrumbs sx={{ mb: 3 }}>
        <Link component={RouterLink} underline="hover" color="inherit" to="/app/home" sx={{ display: 'flex', alignItems: 'center' }}>
          Home
        </Link>
        <Typography color="text.primary" sx={{ display: 'flex', alignItems: 'center', fontWeight: 600 }}>
          Notebook
        </Typography>
      </Breadcrumbs>

      <Stack spacing={3} sx={{ flex: 1, minHeight: 0 }}>
        {/* Header Section */}
        <Paper 
          variant="outlined" 
          sx={{ 
            p: 2.5, 
            borderRadius: 2, 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center',
            bgcolor: 'background.paper',
            border: '1px solid',
            borderColor: 'divider',
            boxShadow: '0 2px 10px rgba(0,0,0,0.02)'
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Box sx={{ p: 1, borderRadius: 1.5, bgcolor: 'primary.light', color: 'primary.main', display: 'flex' }}>
              <NotebookIcon />
            </Box>
            <Box>
              <Typography variant="h5" fontWeight={800} color="primary.main">
                Notebook
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>
                Run interactive Jupyter Notebooks and prototype models directly on your data lake.
              </Typography>
            </Box>
          </Box>
          <Stack direction="row" spacing={1.5}>
            <Button
              variant="outlined"
              startIcon={<RefreshIcon />}
              onClick={fetchNotebookUrl}
              sx={{ borderRadius: 2 }}
            >
              Refresh
            </Button>
            <Button
              component="a"
              href={notebookUrl}
              target="_blank"
              rel="noreferrer"
              variant="contained"
              startIcon={<OpenInNewIcon />}
              disabled={!notebookUrl}
              sx={{ borderRadius: 2, px: 3 }}
            >
              Open Notebook
            </Button>
          </Stack>
        </Paper>

        {loading && <Skeleton variant="rectangular" sx={{ flex: 1, minHeight: 0, borderRadius: 2 }} />}

        {!loading && error && (
          <Box sx={{ p: 0 }}>
            <Alert
              severity="error"
              action={
                <Button color="inherit" size="small" startIcon={<RefreshIcon />} onClick={fetchNotebookUrl}>
                  Retry
                </Button>
              }
              sx={{ borderRadius: 2 }}
            >
              {error}
            </Alert>
          </Box>
        )}

        {!loading && !error && notebookUrl && (
          <Paper
            variant="outlined"
            sx={{
              flex: 1,
              minHeight: 0,
              border: '1px solid',
              borderColor: 'divider',
              borderRadius: 2,
              overflow: 'hidden',
              display: 'flex',
              flexDirection: 'column'
            }}
          >
            <Box
              component="iframe"
              title="Jupyter Notebook"
              src={notebookUrl}
              allowFullScreen
              sx={{
                flex: 1,
                width: "100%",
                height: "100%",
                border: 0,
                bgcolor: "#FFFFFF",
              }}
            />
          </Paper>
        )}
      </Stack>
    </Box>
  );
}

export default Notebook;
