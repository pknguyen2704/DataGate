import { createTheme } from "@mui/material/styles";

const APP_BAR_HEIGHT = 64;
const SIDEBAR_WIDTH = 260;
const BASE_RADIUS = 12;

export const datagateColors = {
  pageBackground: "#F8FAFC",
  pageBackgroundSoft: "#F1F5F9",
  pageGradient:
    "radial-gradient(circle at top left, rgba(37,99,235,0.08), transparent 30%), linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%)",
  cardBorder: "#E2E8F0",
  cardBorderSoft: "#F1F5F9",
  cardBackground: "#FFFFFF",
  cardBackgroundMuted: "#F8FAFC",
  selectedBackground: "rgba(37, 99, 235, 0.08)",
  selectedBorder: "#2563EB",
  tableHeadBackground: "#F1F5F9",
  textPrimary: "#0F172A",
  textSecondary: "#475569",
  accentAmber: "#F59E0B",
  accentBlue: "#3B82F6",
  accentBlueDeep: "#1E40AF",
  success: "#10B981",
  warning: "#F59E0B",
  error: "#EF4444",
};

export const datagateLayout = {
  pagePadding: { xs: 2, md: 3 },
  sectionGap: 3,
  panelRadius: 1.5,
};

export const pageShellSx = {
  p: datagateLayout.pagePadding,
  height: "100%",
  overflow: "auto",
  bgcolor: datagateColors.pageBackground,
  backgroundImage: datagateColors.pageGradient,
};

export const panelSx = {
  borderRadius: datagateLayout.panelRadius,
  border: `1px solid ${datagateColors.cardBorderSoft}`,
  boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03)",
  backgroundColor: datagateColors.cardBackground,
};

export const sectionHeaderSx = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  gap: 2,
};

export const subtlePanelSx = {
  borderRadius: datagateLayout.panelRadius,
  border: `1px solid ${datagateColors.cardBorder}`,
  bgcolor: datagateColors.cardBackgroundMuted,
};

const theme = createTheme({
  spacing: 8,
  palette: {
    mode: 'light',
    primary: {
      main: "#1E40AF",
      light: "#3B82F6",
      dark: "#1E3A8A",
      contrastText: "#FFFFFF",
    },
    secondary: {
      main: "#F59E0B",
    },
    error: {
      main: datagateColors.error,
    },
    warning: {
      main: datagateColors.warning,
    },
    info: {
      main: "#3B82F6",
    },
    success: {
      main: datagateColors.success,
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
    fontFamily: '"Fira Sans", "Outfit", "system-ui", "-apple-system", "Segoe UI", sans-serif',
    h1: {
      fontSize: "4.5rem",
      lineHeight: 1.02,
      fontWeight: 800,
      letterSpacing: "-0.05em",
    },
    h2: {
      fontSize: "3.5rem",
      lineHeight: 1.06,
      fontWeight: 800,
      letterSpacing: "-0.045em",
    },
    h3: {
      fontSize: "2.5rem",
      lineHeight: 1.1,
      fontWeight: 800,
      letterSpacing: "-0.04em",
    },
    h4: {
      fontSize: "2rem",
      lineHeight: 1.15,
      fontWeight: 700,
      letterSpacing: "-0.03em",
    },
    h5: {
      fontSize: "1.5rem",
      lineHeight: 1.2,
      fontWeight: 700,
      letterSpacing: "-0.02em",
    },
    h6: {
      fontSize: "1.125rem",
      lineHeight: 1.3,
      fontWeight: 700,
      letterSpacing: "-0.015em",
    },
    subtitle1: {
      fontSize: "1rem",
      lineHeight: 1.45,
      fontWeight: 600,
      letterSpacing: "-0.01em",
    },
    subtitle2: {
      fontSize: "0.875rem",
      lineHeight: 1.4,
      fontWeight: 600,
    },
    body1: {
      fontSize: "1rem",
      lineHeight: 1.6,
      fontWeight: 400,
    },
    body2: {
      fontSize: "0.875rem",
      lineHeight: 1.55,
      fontWeight: 400,
    },
    caption: {
      fontSize: "0.75rem",
      lineHeight: 1.4,
      fontWeight: 500,
    },
    overline: {
      fontSize: "0.75rem",
      lineHeight: 1.4,
      fontWeight: 700,
      letterSpacing: "0.12em",
      textTransform: "uppercase",
    },
    button: {
      fontSize: "0.9375rem",
      lineHeight: 1.2,
      fontWeight: 700,
      letterSpacing: "-0.01em",
      textTransform: "none",
    },
  },
  shape: {
    borderRadius: BASE_RADIUS,
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        html: {
          fontSize: "16px",
        },
        body: {
          backgroundColor: datagateColors.pageBackground,
          backgroundImage: datagateColors.pageGradient,
          color: datagateColors.textPrimary,
          fontFamily: '"Fira Sans", "Outfit", "system-ui", "-apple-system", "Segoe UI", sans-serif',
          margin: 0,
          WebkitFontSmoothing: "antialiased",
          MozOsxFontSmoothing: "grayscale",
          "&::-webkit-scrollbar": {
            width: "8px",
            height: "8px",
          },
          "&::-webkit-scrollbar-track": {
            background: "transparent",
          },
          "&::-webkit-scrollbar-thumb": {
            background: datagateColors.cardBorder,
            borderRadius: "999px",
          },
        },
        ".glass-card": {
          background: "rgba(255, 255, 255, 0.82)",
          backdropFilter: "blur(12px)",
          WebkitBackdropFilter: "blur(12px)",
          border: "1px solid rgba(226, 232, 240, 0.9)",
          boxShadow: "0 14px 32px rgba(2, 6, 23, 0.08)",
        },
      },
    },
    MuiContainer: {
      styleOverrides: {
        root: {
          marginLeft: 0,
          paddingLeft: "0 !important",
          paddingRight: "0 !important",
          maxWidth: "100% !important",
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
          boxShadow: "none",
          border: `1px solid ${datagateColors.cardBorderSoft}`,
          borderRadius: BASE_RADIUS,
          color: datagateColors.textPrimary,
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
          padding: "10px 18px",
          borderRadius: `${BASE_RADIUS}px`,
          boxShadow: "none",
        },
        sizeSmall: {
          minHeight: 32,
          padding: "6px 12px",
          fontSize: "0.8125rem",
        },
        sizeLarge: {
          minHeight: 48,
          padding: "12px 24px",
          fontSize: "1rem",
        },
        contained: {
          background: "linear-gradient(135deg, #1E40AF 0%, #1D4ED8 100%)",
          "&:hover": {
            boxShadow: "0 16px 30px rgba(30, 64, 175, 0.35)",
            background: "linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%)",
          },
        },
        outlined: {
          borderColor: datagateColors.cardBorder,
          "&:hover": {
            borderColor: datagateColors.selectedBorder,
            backgroundColor: "rgba(59, 130, 246, 0.08)",
          },
        },
      },
    },
    MuiIconButton: {
      styleOverrides: {
        root: {
          borderRadius: `${BASE_RADIUS}px`,
        },
        sizeSmall: {
          padding: 6,
        },
      },
    },
    MuiTextField: {
      defaultProps: {
        size: "medium",
      },
    },
    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          minHeight: 44,
          borderRadius: `${BASE_RADIUS}px`,
          backgroundColor: datagateColors.cardBackgroundMuted,
          "& .MuiOutlinedInput-notchedOutline": {
            borderColor: datagateColors.cardBorder,
          },
          "&:hover .MuiOutlinedInput-notchedOutline": {
            borderColor: datagateColors.selectedBorder,
          },
          "&.Mui-focused .MuiOutlinedInput-notchedOutline": {
            borderWidth: 1,
            borderColor: "#3B82F6",
          },
        },
        input: {
          padding: "12px 14px",
          fontSize: "0.9375rem",
        },
      },
    },
    MuiInputLabel: {
      styleOverrides: {
        root: {
          fontSize: "0.9375rem",
        },
      },
    },
    MuiSelect: {
      styleOverrides: {
        select: {
          display: "flex",
          alignItems: "center",
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          height: 30,
          borderRadius: `${BASE_RADIUS}px`,
          fontSize: "0.8125rem",
          fontWeight: 600,
        },
        sizeSmall: {
          height: 24,
          fontSize: "0.75rem",
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        head: {
          fontSize: "0.8125rem",
          fontWeight: 700,
          color: datagateColors.textSecondary,
          paddingTop: 14,
          paddingBottom: 14,
          backgroundColor: datagateColors.tableHeadBackground,
        },
        body: {
          fontSize: "0.9375rem",
          paddingTop: 16,
          paddingBottom: 16,
        },
      },
    },
    MuiTabs: {
      styleOverrides: {
        indicator: {
          height: 3,
          borderRadius: 999,
        },
      },
    },
    MuiTab: {
      styleOverrides: {
        root: {
          minHeight: 44,
          fontSize: "0.9375rem",
          fontWeight: 600,
          textTransform: "none",
          color: datagateColors.textSecondary,
          "&.Mui-selected": {
            color: datagateColors.textPrimary,
          },
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
          borderRadius: `${BASE_RADIUS}px`,
          "&.Mui-selected": {
            backgroundColor: "rgba(37, 99, 235, 0.18)",
            color: "#93C5FD",
            "& .MuiListItemIcon-root": {
              color: "#93C5FD",
            },
            "&:hover": {
              backgroundColor: "rgba(59, 130, 246, 0.22)",
            },
          },
        },
      },
    },
    MuiDialog: {
      styleOverrides: {
        paper: {
          borderRadius: `${BASE_RADIUS}px`,
          backgroundColor: datagateColors.cardBackground,
        },
      },
    },
    MuiMenu: {
      styleOverrides: {
        paper: {
          borderRadius: `${BASE_RADIUS}px`,
          border: `1px solid ${datagateColors.cardBorderSoft}`,
          backgroundColor: datagateColors.cardBackground,
          boxShadow: "0 18px 40px rgba(2, 6, 23, 0.08)",
        },
      },
    },
    MuiTooltip: {
      styleOverrides: {
        tooltip: {
          fontSize: "0.75rem",
          borderRadius: `${BASE_RADIUS}px`,
        },
      },
    },
  },
  datagate: {
    appBarHeight: `${APP_BAR_HEIGHT}px`,
    sidebarWidth: `${SIDEBAR_WIDTH}px`,
    radii: {
      sm: 8,
      md: 12,
      lg: 16,
      xl: 20,
    },
    fontSizes: {
      xs: "0.75rem",
      sm: "0.875rem",
      md: "0.9375rem",
      base: "1rem",
      lg: "1.125rem",
      xl: "1.5rem",
      "2xl": "2rem",
      "3xl": "2.5rem",
      "4xl": "3.5rem",
    },
  },
});

export default theme;
