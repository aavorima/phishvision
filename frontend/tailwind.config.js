/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Primary - Professional Blue
        primary: {
          DEFAULT: '#3B82F6',
          50: '#EFF6FF',
          100: '#DBEAFE',
          200: '#BFDBFE',
          300: '#93C5FD',
          400: '#60A5FA',
          500: '#3B82F6',
          600: '#2563EB',
          700: '#1D4ED8',
          dim: '#2563EB',
          glow: 'rgba(59, 130, 246, 0.15)',
          subtle: 'rgba(59, 130, 246, 0.08)',
        },
        // Accent - Indigo (clean SaaS style)
        accent: {
          DEFAULT: '#6366F1',
          dim: '#4F46E5',
          glow: 'rgba(99, 102, 241, 0.15)',
        },
        // Success - Neon Green
        success: {
          DEFAULT: '#00ff88',
          dim: '#00cc6a',
          glow: 'rgba(0, 255, 136, 0.15)',
        },
        // Warning - Electric Amber
        warning: {
          DEFAULT: '#ffaa00',
          dim: '#cc8800',
          glow: 'rgba(255, 170, 0, 0.15)',
        },
        // Danger - Signal Red
        danger: {
          DEFAULT: '#ff3366',
          dim: '#cc2952',
          glow: 'rgba(255, 51, 102, 0.15)',
        },
        // Surfaces - Dark Theme
        surface: {
          1: '#0a0a0f',
          2: '#12121a',
          3: '#1a1a24',
          4: '#24242f',
          5: '#2e2e3a',
        },
        // Surfaces - Light Theme
        'surface-light': {
          1: '#ffffff',
          2: '#f8f9fc',
          3: '#f0f2f7',
          4: '#e8eaf0',
          5: '#dde0e8',
        },
      },
      fontFamily: {
        sans: ['Outfit', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'monospace'],
      },
      fontSize: {
        '2xs': ['0.625rem', { lineHeight: '0.875rem' }],
      },
      borderRadius: {
        'xl': '1rem',
        '2xl': '1.25rem',
        '3xl': '1.5rem',
      },
      boxShadow: {
        'glow': '0 0 40px -10px var(--color-primary)',
        'glow-primary': '0 0 30px -5px rgba(59, 130, 246, 0.3)',
        'glow-danger': '0 0 30px -5px rgba(255, 51, 102, 0.3)',
        'glow-success': '0 0 30px -5px rgba(0, 255, 136, 0.3)',
        'glow-warning': '0 0 30px -5px rgba(255, 170, 0, 0.3)',
        'card': '0 4px 24px -4px rgba(0, 0, 0, 0.3)',
        'elevated': '0 8px 40px -8px rgba(0, 0, 0, 0.4)',
      },
      animation: {
        'fade-in-up': 'fadeInUp 0.5s ease-out forwards',
        'fade-in': 'fadeIn 0.3s ease-out forwards',
        'slide-in-left': 'slideInLeft 0.4s ease-out forwards',
        'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
        'shimmer': 'shimmer 2s infinite',
        'float': 'float 3s ease-in-out infinite',
        'spin-slow': 'spin 3s linear infinite',
      },
      keyframes: {
        fadeInUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideInLeft: {
          '0%': { opacity: '0', transform: 'translateX(-20px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        'pulse-glow': {
          '0%, 100%': { opacity: '1', boxShadow: '0 0 20px -5px currentColor' },
          '50%': { opacity: '0.7', boxShadow: '0 0 30px -5px currentColor' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
      },
      backdropBlur: {
        xs: '2px',
      },
      transitionTimingFunction: {
        'spring': 'cubic-bezier(0.175, 0.885, 0.32, 1.275)',
      },
    },
  },
  plugins: [],
}
