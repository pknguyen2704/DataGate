import React from "react";
import { Box, useTheme } from "@mui/material";
import { Outlet } from "react-router-dom";
import SideBar from "~/components/Sidebar/SideBar";
import AppBar from "~/components/AppBar/AppBar";

const MainLayout = () => {
  const theme = useTheme();

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        height: "100vh",
        bgcolor: "background.default",
      }}
    >
      {/* Navbar section */}
      <AppBar />

      {/* Main Layout Area */}
      <Box
        sx={{
          display: "flex",
          pt: theme.datagate.appBarHeight,
          flexGrow: 1,
          overflow: "hidden",
        }}
      >
        {/* Sidebar for quick access to tables */}
        <SideBar />

        {/* Content area */}
        <Box
          component="main"
          sx={{
            flexGrow: 1,
            p: 3,
            overflowY: "auto",
            bgcolor: "#F8FAFC",
            boxShadow: "inset 1px 0 3px rgba(0,0,0,0.02)",
          }}
        >
          <Outlet />
        </Box>
      </Box>
    </Box>
  );
};

export default MainLayout;
