// Professional Security Dashboard Color Palette
// Inspired by KnowBe4, Gophish, and CISA standards

export const colors = {
  // Primary brand colors - Navy Blue (Trust & Authority)
  primary: {
    50: '#eff6ff',
    100: '#dbeafe',
    200: '#bfdbfe',
    300: '#93c5fd',
    400: '#60a5fa',
    500: '#3b82f6',  // Main primary
    600: '#2563eb',
    700: '#1d4ed8',
    800: '#1e40af',
    900: '#1e3a8a',
  },

  // Status colors - CISA compliant
  success: {
    light: '#d1fae5',
    main: '#10b981',   // Green - Safe, resolved
    dark: '#059669',
  },

  warning: {
    light: '#fef3c7',
    main: '#f59e0b',   // Amber - Caution, medium risk
    dark: '#d97706',
  },

  danger: {
    light: '#fee2e2',
    main: '#ef4444',   // Red - Critical, high risk
    dark: '#dc2626',
  },

  info: {
    light: '#dbeafe',
    main: '#3b82f6',   // Blue - Informational
    dark: '#2563eb',
  },

  // Light theme
  light: {
    background: '#f8fafc',      // Slate 50
    surface: '#ffffff',
    surfaceSecondary: '#f1f5f9', // Slate 100
    border: '#e2e8f0',          // Slate 200
    borderDark: '#cbd5e1',      // Slate 300
    text: {
      primary: '#0f172a',       // Slate 900
      secondary: '#475569',     // Slate 600
      tertiary: '#94a3b8',      // Slate 400
    },
  },

  // Dark theme
  dark: {
    background: '#0f172a',      // Slate 900
    surface: '#1e293b',         // Slate 800
    surfaceSecondary: '#334155', // Slate 700
    border: '#334155',          // Slate 700
    borderDark: '#475569',      // Slate 600
    text: {
      primary: '#f8fafc',       // Slate 50
      secondary: '#cbd5e1',     // Slate 300
      tertiary: '#64748b',      // Slate 500
    },
  },

  // Risk level colors
  risk: {
    low: '#10b981',      // Green
    medium: '#f59e0b',   // Amber
    high: '#f97316',     // Orange
    critical: '#ef4444', // Red
  },

  // Severity colors for incidents
  severity: {
    critical: '#dc2626',
    high: '#f97316',
    medium: '#eab308',
    low: '#22c55e',
  },
};

// Helper function to get theme colors
export const getThemeColors = (isDark) => isDark ? colors.dark : colors.light;

// CSS class helpers for common patterns
export const getStatusClasses = (status, isDark) => {
  const base = {
    safe: {
      bg: isDark ? 'bg-green-900/30' : 'bg-green-100',
      text: isDark ? 'text-green-400' : 'text-green-700',
      border: isDark ? 'border-green-800' : 'border-green-200',
    },
    suspicious: {
      bg: isDark ? 'bg-yellow-900/30' : 'bg-yellow-100',
      text: isDark ? 'text-yellow-400' : 'text-yellow-700',
      border: isDark ? 'border-yellow-800' : 'border-yellow-200',
    },
    malicious: {
      bg: isDark ? 'bg-red-900/30' : 'bg-red-100',
      text: isDark ? 'text-red-400' : 'text-red-700',
      border: isDark ? 'border-red-800' : 'border-red-200',
    },
  };
  return base[status] || base.safe;
};

export default colors;
