import { createTheme } from "@mui/material/styles";

const APP_BAR_HEIGHT = "64px";
const SIDEBAR_WIDTH = "260px";

const theme = createTheme({
  palette: {
    primary: {
      main: "#2563EB", // Brand Blue
      light: "#60A5FA",
      dark: "#1E40AF",
      contrastText: "#ffffff",
    },
    secondary: {
      main: "#3B82F6", // Modern Blue
    },
    error: {
      main: "#EF4444",
    },
    warning: {
      main: "#F59E0B",
    },
    info: {
      main: "#3B82F6",
    },
    background: {
      default: "#F1F5F9", // Light gray/slate background for the app
      paper: "#FFFFFF",
    },
    text: {
      primary: "#1E293B",
      secondary: "#64748B",
    },
    divider: "#E2E8F0",
  },
  typography: {
    fontFamily: '"Outfit", "system-ui", "-apple-system", sans-serif',
    h1: { fontWeight: 900, letterSpacing: '-0.025em' },
    h2: { fontWeight: 800, letterSpacing: '-0.025em' },
    h3: { fontWeight: 800, letterSpacing: '-0.025em' },
    h4: { fontWeight: 700, letterSpacing: '-0.02em' },
    h5: { fontWeight: 700 },
    h6: { fontWeight: 700 },
    subtitle1: { fontWeight: 700 },
    subtitle2: { fontWeight: 700 },
    body1: { lineHeight: 1.6 },
    button: {
      textTransform: "none",
      fontWeight: 700,
    },
  },
  shape: {
    borderRadius: 6, // Slightly rounded for a modern, gentle feel
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          backgroundColor: "#F1F5F9",
          fontFamily: '"Outfit", "system-ui", "-apple-system", sans-serif',
          margin: 0,
          WebkitFontSmoothing: 'antialiased',
          MozOsxFontSmoothing: 'grayscale',
          '&::-webkit-scrollbar': {
            width: '6px',
            height: '6px',
          },
          '&::-webkit-scrollbar-track': {
            background: 'transparent',
          },
          '&::-webkit-scrollbar-thumb': {
            background: '#CBD5E1',
            borderRadius: '10px',
          },
        },
        '.glass-card': {
          background: "rgba(255, 255, 255, 0.8)",
          backdropFilter: 'blur(8px)',
          WebkitBackdropFilter: 'blur(8px)',
          border: 'none',
          boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.05)',
        },
      },
    },
    MuiContainer: {
      styleOverrides: {
        root: {
          marginLeft: 0, 
          paddingLeft: '0 !important',
          paddingRight: '0 !important',
          maxWidth: '100% !important',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: "4px",
          padding: "8px 20px",
          boxShadow: 'none',
          "&:hover": {
            boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          boxShadow: 'none',
          border: 'none',
          borderRadius: '4px',
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: "white",
          color: "#1E293B",
          boxShadow: "none",
          borderBottom: "none",
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundColor: "#FFFFFF",
          borderRight: "1px solid #E2E8F0",
        }
      }
    },
    MuiListItemButton: {
      styleOverrides: {
        root: {
          borderRadius: '4px',
          '&.Mui-selected': {
            backgroundColor: '#EFF6FF',
            color: '#2563EB',
            '& .MuiListItemIcon-root': {
              color: '#2563EB',
            },
            '&:hover': {
              backgroundColor: '#DBEAFE',
            }
          }
        }
      }
    }
  },
  datagate: {
    appBarHeight: APP_BAR_HEIGHT,
    sidebarWidth: SIDEBAR_WIDTH,
  },
});

export default theme;