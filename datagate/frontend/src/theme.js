import { createTheme } from "@mui/material/styles";

const APP_BAR_HEIGHT = 64;
const SIDEBAR_WIDTH = 280;
const BASE_RADIUS = 12;

export const datagateColors = {
  shell: "#0F172A",
  shellSoft: "#1E293B",
  shellLine: "#334155",
  pageBackground: "#F1F5F9",
  cardBackground: "#FFFFFF",
  cardBackgroundMuted: "#F8FAFC",
  cardBorder: "rgba(15, 23, 42, 0.15)",
  cardBorderSoft: "rgba(15, 23, 42, 0.08)",
  tableHeadBackground: "#1E40AF",
  textPrimary: "#0F172A",
  textSecondary: "#334155",
  primary: "#1E40AF",
  primaryLight: "#3B82F6",
  primaryDark: "#1E3A8A",
  accentBlue: "#2563EB",
  success: "#10B981",
  warning: "#F59E0B",
  error: "#EF4444",
  statTones: {
    blue: { background: "#EFF6FF", border: "#BFDBFE", accent: "#2563EB" },
    green: { background: "#ECFDF5", border: "#A7F3D0", accent: "#059669" },
    amber: { background: "#FFFBEB", border: "#FDE68A", accent: "#D97706" },
    red: { background: "#FEF2F2", border: "#FECACA", accent: "#DC2626" },
  },
};

const fontFamily = '"Fira Sans", "Outfit", system-ui, -apple-system, "Segoe UI", sans-serif';

const theme = createTheme({
  spacing: 8,
  shape: {
    borderRadius: BASE_RADIUS,
  },
  palette: {
    mode: "light",
    primary: {
      main: datagateColors.primary,
      light: datagateColors.primaryLight,
      dark: datagateColors.primaryDark,
      contrastText: "#FFFFFF",
    },
    secondary: {
      main: datagateColors.warning,
    },
    success: {
      main: datagateColors.success,
    },
    warning: {
      main: datagateColors.warning,
    },
    error: {
      main: datagateColors.error,
    },
    info: {
      main: datagateColors.primaryLight,
    },
    background: {
      default: datagateColors.pageBackground,
      paper: datagateColors.cardBackground,
    },
    text: {
      primary: datagateColors.textPrimary,
      secondary: datagateColors.textSecondary,
    },
    divider: datagateColors.cardBorderSoft,
  },
  typography: {
    fontFamily,
    allVariants: {
      letterSpacing: 0,
    },
    h1: { fontSize: "4.5rem", fontWeight: 800, lineHeight: 1.02 },
    h2: { fontSize: "3.5rem", fontWeight: 800, lineHeight: 1.06 },
    h3: { fontSize: "2.5rem", fontWeight: 800, lineHeight: 1.1 },
    h4: { fontSize: "2rem", fontWeight: 700, lineHeight: 1.15 },
    h5: { fontSize: "1.5rem", fontWeight: 700, lineHeight: 1.2 },
    h6: { fontSize: "1.125rem", fontWeight: 700, lineHeight: 1.3 },
    body1: { fontSize: "1rem", lineHeight: 1.6 },
    body2: { fontSize: "0.875rem", lineHeight: 1.55 },
    button: { fontWeight: 700, textTransform: "none" },
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          margin: 0,
          color: datagateColors.textPrimary,
          backgroundColor: datagateColors.pageBackground,
          fontFamily,
          WebkitFontSmoothing: "antialiased",
          MozOsxFontSmoothing: "grayscale",
        },
      },
    },
    MuiPaper: {
      defaultProps: {
        elevation: 0,
      },
      styleOverrides: {
        root: {
          backgroundImage: "none",
          borderRadius: BASE_RADIUS,
        },
      },
    },
    MuiButton: {
      defaultProps: {
        disableElevation: true,
      },
      styleOverrides: {
        root: {
          minHeight: 40,
          borderRadius: 999,
          fontWeight: 700,
          textTransform: "none",
        },
        sizeSmall: {
          minHeight: 32,
          fontSize: "0.8125rem",
        },
      },
    },
    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          minHeight: 40,
          borderRadius: BASE_RADIUS,
          backgroundColor: datagateColors.cardBackground,
          "& .MuiOutlinedInput-notchedOutline": {
            borderColor: datagateColors.cardBorder,
          },
          "&.Mui-focused .MuiOutlinedInput-notchedOutline": {
            borderColor: datagateColors.accentBlue,
            borderWidth: 1,
          },
        },
        input: {
          padding: "10px 14px",
          fontSize: "0.875rem",
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: BASE_RADIUS,
          fontWeight: 600,
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        head: {
          color: "#FFFFFF",
          fontWeight: 700,
          backgroundColor: datagateColors.tableHeadBackground,
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundColor: datagateColors.cardBackground,
          borderRight: `1px solid ${datagateColors.cardBorderSoft}`,
        },
      },
    },
    MuiListItemButton: {
      styleOverrides: {
        root: {
          minHeight: 44,
          borderRadius: BASE_RADIUS,
          "&.Mui-selected": {
            color: datagateColors.primary,
            backgroundColor: "rgba(37, 99, 235, 0.18)",
            "& .MuiListItemIcon-root": {
              color: datagateColors.primary,
            },
          },
        },
      },
    },
  },
  datagate: {
    appBarHeight: `${APP_BAR_HEIGHT}px`,
    sidebarWidth: `${SIDEBAR_WIDTH}px`,
    radii: {
      sm: 12,
      md: 16,
      lg: 24,
    },
  },
});

export default theme;
