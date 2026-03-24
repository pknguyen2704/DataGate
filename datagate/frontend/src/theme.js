import { createTheme } from "@mui/material/styles";

const APP_BAR_HEIGHT = "64px";
const FOOTER_HEIGHT = "48px";
const SIDEBAR_WIDTH = "260px";

const theme = createTheme({
  palette: {
    primary: {
      main: "#1E40AF", // Deep Blue from design system
      light: "#3B82F6",
      dark: "#1E3A8A",
      contrastText: "#ffffff",
    },
    secondary: {
      main: "#22C55E", // Green accent for CTA as suggested by design system
    },
    background: {
      default: "#ffffff", // Pure white background as requested
      paper: "#ffffff",
    },
    text: {
      primary: "#1E3A8A", // Deep blue text for better contrast on white
      secondary: "#64748B",
    },
    divider: "#E2E8F0",
  },
  typography: {
    fontFamily: '"Open Sans", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: { fontFamily: '"Poppins", sans-serif', fontWeight: 700 },
    h2: { fontFamily: '"Poppins", sans-serif', fontWeight: 700 },
    h3: { fontFamily: '"Poppins", sans-serif', fontWeight: 600 },
    h4: { fontFamily: '"Poppins", sans-serif', fontWeight: 600 },
    h5: { fontFamily: '"Poppins", sans-serif', fontWeight: 600 },
    h6: { fontFamily: '"Poppins", sans-serif', fontWeight: 600 },
    button: {
      textTransform: "none",
      fontWeight: 600,
    },
  },
  shape: {
    borderRadius: 1, // Strictly <= 1 as requested
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 1,
          padding: "8px 16px",
          transition: "all 250ms cubic-bezier(0.4, 0, 0.2, 1)",
          "&:hover": {
            transform: "translateY(-1px)",
            boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)",
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 1,
          boxShadow: "0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)",
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: "#1E40AF",
          boxShadow: "none",
          borderBottom: "1px solid #E2E8F0",
        },
      },
    },
  },
  datagate: {
    appBarHeight: APP_BAR_HEIGHT,
    footerHeight: FOOTER_HEIGHT,
    sidebarWidth: SIDEBAR_WIDTH,
  },
});

export default theme;