import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "media",
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Primary brand — the PDFForge orange.
        brand: {
          50: "#fff5f0",
          100: "#ffe8dc",
          200: "#ffcbb0",
          300: "#ffa884",
          400: "#ff7f4d",
          500: "#f75f22",
          600: "#e64e12",
          700: "#bf3d0f",
          800: "#983312",
          900: "#7a2d13",
        },
        // Deep teal used for the workspace sidebar and ink accents.
        ink: {
          50: "#eef5f3",
          100: "#d4e6e2",
          200: "#a7cdc6",
          300: "#6faba1",
          400: "#3f867b",
          500: "#2a6d63",
          600: "#1d514a",
          700: "#163f3a",
          800: "#102e2b",
          900: "#0b211f",
        },
      },
      fontFamily: {
        sans: [
          '"Plus Jakarta Sans"',
          "ui-sans-serif",
          "system-ui",
          "-apple-system",
          "Segoe UI",
          "Roboto",
          "sans-serif",
        ],
      },
      boxShadow: {
        card: "0 1px 2px rgba(16,24,40,0.04), 0 8px 24px rgba(16,24,40,0.06)",
        lift: "0 16px 40px -18px rgba(16,24,40,0.28)",
        brand: "0 12px 26px -10px rgba(230,78,18,0.45)",
      },
      borderRadius: {
        "2xl": "1rem",
        "3xl": "1.5rem",
      },
    },
  },
  plugins: [],
};

export default config;
