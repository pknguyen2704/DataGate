import { createTheme } from "@mui/material/styles";

const APP_BAR_HEIGHT = 64;
const SIDEBAR_WIDTH = 280;
const BASE_RADIUS = 12;

export const datagateColors = {
  shell: "#0F172A",
  shellSoft: "#1E293B",
  shellLine: "#334155",
  pageBackground: "#F1F5F9",
  pageBackgroundSoft: "#FFFFFF",
  pageGradient: "linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%)",
  cardBorder: "rgba(15, 23, 42, 0.15)",
  cardBorderSoft: "rgba(15, 23, 42, 0.08)",
  cardBackground: "#FFFFFF",
  cardBackgroundMuted: "#F8FAFC",
  selectedBackground: "rgba(37, 99, 235, 0.08)",
  selectedBorder: "#2563EB",
  tableHeadBackground: "#1E40AF",
  textPrimary: "#0F172A",
  textSecondary: "#334155",
  accentAmber: "#F59E0B",
  accentBlue: "#2563EB",
  accentBlueDeep: "#1D4ED8",
  success: "#10B981",
  warning: "#F59E0B",
  error: "#EF4444",
  glass: {
    background: "rgba(255, 255, 255, 0.95)",
    border: "1px solid rgba(15, 23, 42, 0.08)",
    blur: "blur(8px)",
  }
};

export const datagateLayout = {
  pagePadding: { xs: 3, md: 5 },
  sectionGap: 6,
  panelRadius: 1,
};

export const pageShellSx = {
  p: datagateLayout.pagePadding,
  height: "100%",
  overflow: "auto",
  bgcolor: datagateColors.pageBackground,
  backgroundImage: datagateColors.pageGradient,
};

export const panelSx = {
  borderRadius: `${BASE_RADIUS}px`,
  border: datagateColors.glass.border,
  backdropFilter: datagateColors.glass.blur,
  backgroundColor: datagateColors.glass.background,
  boxShadow: "0 8px 32px 0 rgba(31, 38, 135, 0.07)",
  overflow: "hidden",
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
    mode: "light",
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
      letterSpacing: 0,
    },
    h2: {
      fontSize: "3.5rem",
      lineHeight: 1.06,
      fontWeight: 800,
      letterSpacing: 0,
    },
    h3: {
      fontSize: "2.5rem",
      lineHeight: 1.1,
      fontWeight: 800,
      letterSpacing: 0,
    },
    h4: {
      fontSize: "2rem",
      lineHeight: 1.15,
      fontWeight: 700,
      letterSpacing: 0,
    },
    h5: {
      fontSize: "1.5rem",
      lineHeight: 1.2,
      fontWeight: 700,
      letterSpacing: 0,
    },
    h6: {
      fontSize: "1.125rem",
      lineHeight: 1.3,
      fontWeight: 700,
      letterSpacing: 0,
    },
    subtitle1: {
      fontSize: "1rem",
      lineHeight: 1.45,
      fontWeight: 600,
      letterSpacing: 0,
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
      letterSpacing: 0,
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
          background: "#FFFFFF",
          border: `1px solid ${datagateColors.cardBorder}`,
          boxShadow: "0 16px 36px rgba(6, 26, 54, 0.08)",
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
          backgroundColor: "#FFFFFF",
          border: "1px solid",
          borderColor: "rgba(0, 0, 0, 0.08)",
          borderRadius: `${BASE_RADIUS}px`,
          boxShadow: "0 4px 12px rgba(0, 0, 0, 0.03)",
          color: datagateColors.textPrimary,
          "&:hover": {
            boxShadow: "0 8px 30px rgba(0,0,0,0.08)",
          }
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
          padding: "8px 16px",
          borderRadius: "99px",
          boxShadow: "none",
          fontWeight: 600,
          transition: "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)",
          textTransform: "none",
        },
        sizeSmall: {
          minHeight: 32,
          padding: "4px 12px",
          fontSize: "0.8125rem",
        },
        sizeLarge: {
          minHeight: 48,
          padding: "12px 24px",
          fontSize: "1rem",
        },
        contained: {
          background: datagateColors.accentBlue,
          color: "#FFFFFF",
          "&:hover": {
            boxShadow: "0 4px 12px rgba(37, 99, 235, 0.2)",
            background: "#1D4ED8",
            transform: "translateY(-1px)",
          },
          "&:active": {
            transform: "translateY(0)",
          }
        },
        outlined: {
          borderColor: datagateColors.cardBorder,
          color: datagateColors.textPrimary,
          "&:hover": {
            borderColor: datagateColors.selectedBorder,
            backgroundColor: "rgba(37, 99, 235, 0.04)",
            transform: "translateY(-1px)",
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
          minHeight: 40,
          borderRadius: `${BASE_RADIUS}px`,
          backgroundColor: "#FFFFFF",
          transition: "all 0.2s ease",
          "& .MuiOutlinedInput-notchedOutline": {
            borderColor: datagateColors.cardBorder,
            transition: "border-color 0.2s ease",
          },
          "&:hover .MuiOutlinedInput-notchedOutline": {
            borderColor: "#94A3B8",
          },
          "&.Mui-focused": {
            backgroundColor: "#FFFFFF",
            boxShadow: "0 0 0 4px rgba(37, 99, 235, 0.1)",
            "& .MuiOutlinedInput-notchedOutline": {
              borderWidth: 1,
              borderColor: datagateColors.accentBlue,
            },
          },
        },
        input: {
          padding: "10px 14px",
          fontSize: "0.875rem",
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
          fontSize: "0.875rem",
          fontWeight: 700,
          color: "#FFFFFF",
          paddingTop: 14,
          paddingBottom: 14,
          backgroundColor: datagateColors.tableHeadBackground,
          borderBottom: "none",
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
            color: "#1E40AF",
            "& .MuiListItemIcon-root": {
              color: "#1E40AF",
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
      sm: 12,
      md: 16,
      lg: 24,
      xl: 32,
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
