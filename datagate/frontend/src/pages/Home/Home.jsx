import React, { useEffect, useMemo, useState } from "react";
import {
  Box,
  Button,
  CircularProgress,
  Grid,
  MenuItem,
  Paper,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import {
  AdsClickOutlined as ActionIcon,
  DatasetOutlined as DatasetIcon,
  Inventory2Outlined as AssetsIcon,
} from "@mui/icons-material";
import { useNavigate } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import { fetchAssets } from "~/stores/slices/servicesSlice";

const rangeOptions = [
  { label: "Latest", value: "latest" },
  { label: "Yesterday", value: "1d" },
];

const formatName = (user) => user?.full_name || user?.username || user?.email || "there";

function Home() {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const user = useSelector((state) => state.auth.user);
  const assets = useSelector((state) => state.services.assets);
  const assetsStatus = useSelector((state) => state.services.assetsStatus);
  const [range, setRange] = useState("latest");

  useEffect(() => {
    if (assetsStatus === "idle") {
      dispatch(fetchAssets());
    }
  }, [assetsStatus, dispatch]);

  const ownedAssets = assets.slice(0, 8);
  const totalAssets = assets.length;
  const selectedDay = useMemo(() => new Date().getDate(), []);
  const loading = assetsStatus === "loading";

  return (
    <Box sx={{ p: 2, height: "100%", overflow: "auto"}}>
      <Paper
        sx={{
          mb: 4,
          px: { xs: 3, md: 5 },
          py: { xs: 4, md: 6 },
          // borderRadius: ,
          color: "#FFFFFF",
          background: "linear-gradient(135deg, #2E6BFF 0%, #2347D9 55%, #1938CF 100%)",
          boxShadow: "0 30px 60px rgba(28, 70, 217, 0.22)",
        }}
      >
        <Typography
          variant="h2"
          sx={{
            textAlign: "center",
            fontWeight: 800,
            letterSpacing: "-0.04em",
            fontSize: { xs: "2.5rem", md: "4rem" },
          }}
        >
          Welcome, {formatName(user)}!
        </Typography>
      </Paper>

      <Grid container spacing={3}>
        <Grid item xs={12} md={5}>
          <Paper sx={{ borderRadius: 4, overflow: "hidden", minHeight: 540 }}>
            <Stack
              direction="row"
              alignItems="center"
              justifyContent="space-between"
              sx={{ px: 4, py: 3, borderBottom: "1px solid #EEF2F7" }}
            >
              <Stack direction="row" spacing={1.5} alignItems="center">
                <DatasetIcon sx={{ fontSize: 38, color: "#5B6475" }} />
                <Typography variant="h4" sx={{ fontWeight: 500, color: "#424A5B" }}>
                  My Data
                </Typography>
              </Stack>

              <TextField select value={range} onChange={(event) => setRange(event.target.value)} sx={{ minWidth: 180 }}>
                {rangeOptions.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </TextField>
            </Stack>

            <Box sx={{ px: 4, py: 6, textAlign: "center" }}>
              {loading ? (
                <CircularProgress />
              ) : ownedAssets.length === 0 ? (
                <Stack spacing={3} alignItems="center" sx={{ pt: 8 }}>
                  <DatasetIcon sx={{ fontSize: 110, color: "#B0B6C4" }} />
                  <Typography variant="h3" sx={{ fontWeight: 700, color: "#424A5B" }}>
                    No Records
                  </Typography>
                  <Typography sx={{ maxWidth: 430, color: "#6B7280", fontSize: "1.1rem" }}>
                    You have not owned any data yet, explore more data assets to get in place.
                  </Typography>
                  <Button
                    variant="contained"
                    size="large"
                    onClick={() => navigate("/explore")}
                    sx={{ px: 4, py: 1.5, borderRadius: 3, textTransform: "none", fontSize: "1rem" }}
                  >
                    Explore Assets
                  </Button>
                </Stack>
              ) : (
                <Stack spacing={2.5} alignItems="stretch">
                  {ownedAssets.map((asset) => (
                    <Paper
                      key={`${asset.service_id}-${asset.table_name}`}
                      variant="outlined"
                      sx={{ p: 2.5, borderRadius: 3, cursor: "pointer" }}
                      onClick={() => navigate(`/explore?service=${asset.service_id}&table=${encodeURIComponent(asset.table_name)}`)}
                    >
                      <Typography sx={{ fontWeight: 700 }}>{asset.asset_name}</Typography>
                      <Typography color="text.secondary">{asset.schema_name}</Typography>
                    </Paper>
                  ))}
                </Stack>
              )}
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} md={7}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Paper sx={{ borderRadius: 4, overflow: "hidden", minHeight: 540 }}>
                <Stack
                  direction="row"
                  alignItems="center"
                  justifyContent="space-between"
                  sx={{ px: 4, py: 3, borderBottom: "1px solid #EEF2F7" }}
                >
                  <Stack direction="row" spacing={1.5} alignItems="center">
                    <AssetsIcon sx={{ fontSize: 38, color: "#5B6475" }} />
                    <Typography variant="h4" sx={{ fontWeight: 500, color: "#424A5B" }}>
                      Total Data Assets
                    </Typography>
                  </Stack>

                  <TextField select value={"7d"} sx={{ minWidth: 180 }}>
                    <MenuItem value="7d">Last 7 days</MenuItem>
                  </TextField>
                </Stack>

                <Box sx={{ px: 3, py: 4 }}>
                  <Box
                    sx={{
                      width: { xs: 280, md: 500 },
                      height: { xs: 280, md: 500 },
                      mx: "auto",
                      borderRadius: "50%",
                      position: "relative",
                      background:
                        "conic-gradient(#244D99 0deg 300deg, #2B63D9 300deg 331deg, #2E73F0 331deg 346deg, #5090FF 346deg 360deg)",
                    }}
                  >
                    <Box
                      sx={{
                        position: "absolute",
                        inset: { xs: 42, md: 76 },
                        borderRadius: "50%",
                        bgcolor: "#FFFFFF",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                      }}
                    >
                      <Typography sx={{ fontSize: { xs: "2.5rem", md: "4rem" }, fontWeight: 500, color: "#4B5563" }}>
                        {loading ? "--" : totalAssets.toLocaleString()}
                      </Typography>
                    </Box>
                  </Box>

                  <Stack direction="row" spacing={2} justifyContent="center" sx={{ mt: 3, flexWrap: "wrap" }}>
                    {Array.from({ length: 7 }).map((_, index) => {
                      const day = selectedDay - (6 - index);
                      const active = index === 6;
                      return (
                        <Paper
                          key={day}
                          variant="outlined"
                          sx={{
                            width: 88,
                            py: 1.75,
                            textAlign: "center",
                            borderRadius: 3,
                            borderColor: active ? "#2E6BFF" : "#E5EAF2",
                            bgcolor: active ? "#DCEBFF" : "#FFFFFF",
                          }}
                        >
                          <Typography sx={{ fontWeight: 700, fontSize: "1.1rem" }}>{String(day).padStart(2, "0")}</Typography>
                          <Typography sx={{ color: "#718096", fontSize: "0.95rem" }}>Apr</Typography>
                        </Paper>
                      );
                    })}
                  </Stack>
                </Box>
              </Paper>
            </Grid>

            <Grid item xs={12}>
              <Paper sx={{ p: 3.5, borderRadius: 4, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <Stack direction="row" spacing={2} alignItems="center">
                  <ActionIcon sx={{ fontSize: 36, color: "#2347D9" }} />
                  <Box>
                    <Typography variant="h6" sx={{ fontWeight: 700 }}>
                      Continue with Metrics Monitoring
                    </Typography>
                    <Typography color="text.secondary">
                      Review confidence bands, sensitivity tuning, and suggested metrics from profiling history.
                    </Typography>
                  </Box>
                </Stack>
                <Button variant="contained" onClick={() => navigate("/metrics")} sx={{ borderRadius: 3, textTransform: "none", px: 3 }}>
                  Open Metrics
                </Button>
              </Paper>
            </Grid>
          </Grid>
        </Grid>
      </Grid>
    </Box>
  );
}

export default Home;
