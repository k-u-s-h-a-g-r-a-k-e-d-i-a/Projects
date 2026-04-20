/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        midnight:   '#0F1117',
        charcoal:   '#161B22',
        slate:      '#1C2333',
        graphite:   '#242C3A',
        storm:      '#2D3748',
        silver:     '#E2E8F0',
        ash:        '#A0AEC0',
        pewter:     '#718096',
        smoke:      '#4A5568',
        alert:      '#E53E3E',
        caution:    '#ED8936',
        safe:       '#48BB78',
        intel:      '#4299E1',
        forensic:   '#9F7AEA',
      },
      fontFamily: {
        sans: ['Inter', 'Segoe UI', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      borderRadius: {
        sm: '6px',
        md: '10px',
        lg: '16px',
      },
      boxShadow: {
        card: '0 2px 8px rgba(0, 0, 0, 0.3)',
        elevated: '0 8px 24px rgba(0, 0, 0, 0.4)',
      }
    },
  },
  plugins: [],
};
