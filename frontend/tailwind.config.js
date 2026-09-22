/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        // Deep navy/charcoal, not pure black — per design system spec.
        background: "#080D14",
        surface: "#101820",
        "surface-alt": "#151F29",
        "surface-raised": "#1A2530",
        border: "#1E2A38",
        "border-strong": "#293A4A",
        primary: {
          DEFAULT: "#3B9EFF",
          hover: "#2B87E8",
          muted: "#1E3A52",
        },
        accent: "#22D3EE",
        critical: "#E5484D",
        high: "#F0883E",
        medium: "#E8B930",
        low: "#5B8DEF",
        info: "#64748B",
        success: "#2DBE72",
        // Text scale — avoids reaching for arbitrary slate-N everywhere.
        ink: {
          primary: "#E7ECF2",
          secondary: "#9AAAB8",
          tertiary: "#6B7A8A",
          disabled: "#4A5866",
        },
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "ui-monospace", "SFMono-Regular", "monospace"],
      },
      fontSize: {
        "page-title": ["26px", { lineHeight: "32px", fontWeight: "600" }],
        "section-title": ["17px", { lineHeight: "24px", fontWeight: "600" }],
        body: ["13.5px", { lineHeight: "20px" }],
        meta: ["11.5px", { lineHeight: "16px" }],
        code: ["13px", { lineHeight: "20px" }],
      },
      boxShadow: {
        panel: "0 1px 2px 0 rgb(0 0 0 / 0.3)",
        popover: "0 8px 24px -4px rgb(0 0 0 / 0.5)",
      },
    },
  },
  plugins: [],
};
