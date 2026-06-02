/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        surface: "oklch(0.98 0.006 240)",
        ink: "oklch(0.21 0.018 250)",
        muted: "oklch(0.48 0.018 250)",
        line: "oklch(0.88 0.01 250)",
        accent: "oklch(0.47 0.14 235)"
      }
    },
  },
  plugins: [],
};
