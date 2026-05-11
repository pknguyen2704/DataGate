import React from "react";
import { Box, Container } from "@mui/material";
import { Outlet } from "react-router-dom";

const Auth = () => {
  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "linear-gradient(135deg, #061A36 0%, #0B2550 52%, #FFFFFF 52%, #EEF4FB 100%)",
        position: "relative",
        overflow: "hidden",
      }}
    >
      <Container maxWidth="sm">
        <Box
          sx={{
            width: "100%",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            zIndex: 1,
            position: "relative",
          }}
        >
          <Outlet />
        </Box>
      </Container>
    </Box>
  );
};

export default Auth;
