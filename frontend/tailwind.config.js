/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Cyberpunk neon theme
        'neon': {
          'cyan': '#00f5ff',
          'pink': '#ff00ff',
          'purple': '#9d00ff',
          'green': '#00ff9d',
          'yellow': '#f5ff00',
          'orange': '#ff9500',
          'red': '#ff0055',
        },
        'dark': {
          '950': '#0a0a0f',
          '900': '#0d0d14',
          '800': '#12121a',
          '700': '#1a1a24',
          '600': '#24242f',
          '500': '#2f2f3d',
        },
        'bullish': '#00ff9d',
        'bearish': '#ff0055',
        'neutral': '#00f5ff',
      },
      fontFamily: {
        'display': ['Orbitron', 'monospace'],
        'mono': ['JetBrains Mono', 'Fira Code', 'monospace'],
        'sans': ['Rajdhani', 'sans-serif'],
      },
      animation: {
        'glow': 'glow 2s ease-in-out infinite alternate',
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'scan': 'scan 8s linear infinite',
        'float': 'float 6s ease-in-out infinite',
      },
      keyframes: {
        glow: {
          '0%': { boxShadow: '0 0 5px currentColor, 0 0 10px currentColor' },
          '100%': { boxShadow: '0 0 10px currentColor, 0 0 20px currentColor, 0 0 30px currentColor' },
        },
        scan: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100%)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
      },
      backgroundImage: {
        'grid-pattern': `linear-gradient(rgba(0, 245, 255, 0.03) 1px, transparent 1px),
                         linear-gradient(90deg, rgba(0, 245, 255, 0.03) 1px, transparent 1px)`,
        'cyber-gradient': 'linear-gradient(135deg, #0a0a0f 0%, #12121a 50%, #0d0d14 100%)',
      },
      backgroundSize: {
        'grid': '50px 50px',
      },
    },
  },
  plugins: [],
}

