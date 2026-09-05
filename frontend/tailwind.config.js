/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          dark: '#0a0f1d',      // Deep slate blue-black
          card: '#141b2d',      // Cool dark blue card background
          border: '#1f293d',    // Border line color
          text: '#f3f4f6',      // Bright text
          muted: '#9ca3af',     // Muted gray text
        },
        status: {
          safe: '#10b981',      // Emerald Green for Safe
          warning: '#f59e0b',   // Amber for Warning
          critical: '#ef4444',  // Rose Red for Critical Danger
          offline: '#6b7280',   // Gray for disconnected states
        }
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'ping-slow': 'ping 2s cubic-bezier(0, 0, 0.2, 1) infinite',
      }
    },
  },
  plugins: [],
}
