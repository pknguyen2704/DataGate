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
        background: "linear-gradient(135deg, #EFF6FF 0%, #FFFFFF 52%, #DBEAFE 100%)",
        position: "relative",
        overflow: "hidden",
        "&::before": {
          content: '""',
          position: "absolute",
          top: "-10%",
          right: "-10%",
          width: "40%",
          height: "40%",
          background: "rgba(37, 99, 235, 0.08)",
          borderRadius: "50%",
          filter: "blur(80px)",
          animation: "float 20s infinite alternate ease-in-out",
        },
        "&::after": {
          content: '""',
          position: "absolute",
          bottom: "-10%",
          left: "-10%",
          width: "30%",
          height: "30%",
          background: "rgba(59, 130, 246, 0.08)",
          borderRadius: "50%",
          filter: "blur(60px)",
          animation: "float 15s infinite alternate-reverse ease-in-out",
        },
        "@keyframes float": {
          "0%": { transform: "translate(0, 0)" },
          "100%": { transform: "translate(20px, 20px)" },
        },
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
