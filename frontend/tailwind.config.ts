import type { Config } from "tailwindcss";

export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          950: "#101216",
          900: "#171a21",
          800: "#20242d",
          700: "#2d3340",
        },
        brand: {
          50: "#eff6ff",
          700: "#1d4ed8",
          600: "#2563eb",
          500: "#3b82f6",
          400: "#60a5fa",
        },
      },
      boxShadow: {
        soft: "0 18px 48px rgba(15, 23, 42, 0.12)",
      },
    },
  },
  plugins: [],
} satisfies Config;
