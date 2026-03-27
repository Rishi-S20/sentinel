/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#eef9ff",
          100: "#d8f1ff",
          200: "#b9e7ff",
          300: "#89d9ff",
          400: "#52c1ff",
          500: "#2aa2ff",
          600: "#1483f5",
          700: "#0d6be1",
          800: "#1157b6",
          900: "#144a8f",
          950: "#112e57",
        },
        surface: {
          0: "#ffffff",
          50: "#f8fafc",
          100: "#f1f5f9",
          200: "#e2e8f0",
          700: "#334155",
          800: "#1e293b",
          900: "#0f172a",
          950: "#020617",
        },
        bullish: "#22c55e",
        bearish: "#ef4444",
        neutral: "#f59e0b",
      },
    },
  },
  plugins: [],
};
