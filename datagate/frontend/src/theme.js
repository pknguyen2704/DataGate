import { createTheme } from "@mui/material/styles";

const APP_BAR_HEIGHT = 64;
const SIDEBAR_WIDTH = 260;
const BASE_RADIUS = 10;

export const datagateColors = {
  pageBackground: "#F7F9FC",
  cardBorder: "#E5EAF2",
  cardBorderSoft: "#EEF2F7",
  cardBackground: "#FFFFFF",
  cardBackgroundMuted: "#FCFDFE",
  selectedBackground: "#EEF4FF",
  selectedBorder: "#7BA7FF",
  tableHeadBackground: "#F8FAFC",
};

export const datagateLayout = {
  pagePadding: { xs: 2, md: 3 },
  sectionGap: 3,
  panelRadius: 3,
};

export const pageShellSx = {
  p: datagateLayout.pagePadding,
  height: "100%",
  overflow: "auto",
  bgcolor: datagateColors.pageBackground,
};

export const panelSx = {
  borderRadius: datagateLayout.panelRadius,
  border: `1px solid ${datagateColors.cardBorderSoft}`,
  boxShadow: "0 2px 10px rgba(15, 23, 42, 0.03)",
  backgroundColor: datagateColors.cardBackground,
};

export const sectionHeaderSx = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  gap: 2,
};

export const subtlePanelSx = {
  borderRadius: 3,
  border: `1px solid ${datagateColors.cardBorder}`,
  bgcolor: datagateColors.cardBackgroundMuted,
};

const theme = createTheme({
  spacing: 8,
  palette: {
    primary: {
      main: "#2563EB",
      light: "#60A5FA",
      dark: "#1E40AF",
      contrastText: "#FFFFFF",
    },
    secondary: {
      main: "#3B82F6",
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
    success: {
      main: "#16A34A",
    },
    background: {
      default: datagateColors.pageBackground,
      paper: "#FFFFFF",
    },
    text: {
      primary: "#1E293B",
      secondary: "#64748B",
    },
    divider: "#E2E8F0",
  },
  typography: {
    fontFamily: '"Outfit", "system-ui", "-apple-system", "Segoe UI", sans-serif',
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
          color: "#1E293B",
          fontFamily: '"Outfit", "system-ui", "-apple-system", "Segoe UI", sans-serif',
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
            background: "#CBD5E1",
            borderRadius: "999px",
          },
        },
        ".glass-card": {
          background: "rgba(255, 255, 255, 0.82)",
          backdropFilter: "blur(10px)",
          WebkitBackdropFilter: "blur(10px)",
          border: "1px solid rgba(226, 232, 240, 0.8)",
          boxShadow: "0 12px 30px rgba(15, 23, 42, 0.06)",
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
          border: "1px solid #E5EAF2",
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
          padding: "10px 18px",
          borderRadius: 10,
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
          "&:hover": {
            boxShadow: "0 10px 24px rgba(37, 99, 235, 0.18)",
          },
        },
      },
    },
    MuiIconButton: {
      styleOverrides: {
        root: {
          borderRadius: 10,
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
          borderRadius: 14,
          backgroundColor: "#FFFFFF",
          "& .MuiOutlinedInput-notchedOutline": {
            borderColor: "#D8E1EC",
          },
          "&:hover .MuiOutlinedInput-notchedOutline": {
            borderColor: "#B8C5D6",
          },
          "&.Mui-focused .MuiOutlinedInput-notchedOutline": {
            borderWidth: 1,
            borderColor: "#2563EB",
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
          borderRadius: 10,
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
          color: "#475569",
          paddingTop: 14,
          paddingBottom: 14,
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
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundColor: "#FFFFFF",
          borderRight: "1px solid #E2E8F0",
        },
      },
    },
    MuiListItemButton: {
      styleOverrides: {
        root: {
          minHeight: 44,
          borderRadius: 10,
          "&.Mui-selected": {
            backgroundColor: "#EFF6FF",
            color: "#2563EB",
            "& .MuiListItemIcon-root": {
              color: "#2563EB",
            },
            "&:hover": {
              backgroundColor: "#DBEAFE",
            },
          },
        },
      },
    },
    MuiDialog: {
      styleOverrides: {
        paper: {
          borderRadius: 18,
        },
      },
    },
    MuiMenu: {
      styleOverrides: {
        paper: {
          borderRadius: 14,
          border: "1px solid #E5EAF2",
          boxShadow: "0 18px 40px rgba(15, 23, 42, 0.12)",
        },
      },
    },
    MuiTooltip: {
      styleOverrides: {
        tooltip: {
          fontSize: "0.75rem",
          borderRadius: 8,
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
