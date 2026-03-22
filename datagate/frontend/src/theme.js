import { createTheme } from "@mui/material/styles";

const APP_BAR_HEIGHT = "64px";
const FOOTER_HEIGHT = "48px";
const SIDEBAR_WIDTH = "240px";

const theme = createTheme({
  palette: {
    primary: {
      main: "#1a237e", // Deep Blue
      light: "#534bae",
      dark: "#000051",
    },
    secondary: {
      main: "#ff9800", // Gold/Orange
    },
    background: {
      default: "#f4f6f8",
      paper: "#ffffff",
    },
    text: {
      primary: "#263238",
      secondary: "#546e7a",
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h6: {
      fontWeight: 600,
    },
    h4: {
      fontWeight: 700,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: "none",
          borderRadius: 8,
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: "0 4px 20px 0 rgba(0,0,0,0.05)",
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