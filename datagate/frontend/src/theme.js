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
      main: "#10B981", // Success Green
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
      default: "#F8FAFC", // Light gray background
      paper: "#FFFFFF",
    },
    text: {
      primary: "#1E293B",
      secondary: "#64748B",
    },
    divider: "#E2E8F0",
  },
  typography: {
    fontFamily: '"Inter", "system-ui", "-apple-system", sans-serif',
    h1: { fontWeight: 800, letterSpacing: '-0.025em' },
    h2: { fontWeight: 700, letterSpacing: '-0.025em' },
    h3: { fontWeight: 700, letterSpacing: '-0.025em' },
    h4: { fontWeight: 600, letterSpacing: '-0.025em' },
    h5: { fontWeight: 600 },
    h6: { fontWeight: 600 },
    subtitle1: { fontWeight: 500 },
    subtitle2: { fontWeight: 500 },
    body1: { lineHeight: 1.6 },
    button: {
      textTransform: "none",
      fontWeight: 600,
    },
  },
  shape: {
    borderRadius: 12, // 8-12px as requested
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: "8px",
          padding: "8px 20px",
          boxShadow: 'none',
          "&:hover": {
            boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
          },
        },
        containedPrimary: {
          background: 'linear-gradient(135deg, #2563EB 0%, #3B82F6 100%)',
        }
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
          border: '1px solid #E2E8F0',
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: "rgba(255, 255, 255, 0.8)",
          backdropFilter: 'blur(8px)',
          color: "#1E293B",
          boxShadow: "none",
          borderBottom: "1px solid #E2E8F0",
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
          borderRadius: '8px',
          margin: '4px 8px',
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