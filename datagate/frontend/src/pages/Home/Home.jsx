import React from "react";
import { Box, Paper, Stack, Typography } from "@mui/material";
import { useSelector } from "react-redux";
import { pageShellSx, panelSx } from "~/theme";

export default function Home() {
  const { user } = useSelector((state) => state.auth);
  const firstName = user?.full_name?.split(" ")?.[0];

  return (
    <Box sx={pageShellSx}>
      <Paper
        sx={{
          ...panelSx,
          minHeight: "calc(100vh - 160px)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background:
            "radial-gradient(circle at top left, rgba(37, 99, 235, 0.12), transparent 34%), linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%)",
        }}
      >
        <Stack spacing={1.5} sx={{ textAlign: "center", px: 4 }}>
          <Typography variant="overline" color="primary.main">
            DataGate
          </Typography>
          <Typography variant="h3" fontWeight={800}>
            Welcome{firstName ? `, ${firstName}` : ""}
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ maxWidth: 560 }}>
            Lakehouse data quality workspace.
          </Typography>
        </Stack>
      </Paper>
    </Box>
  );
}
