module.exports = {
  content: ["./src/**/templates/**/*.html", "./src/**/*.py"],
  theme: {
    extend: {
      fontFamily: {
        display: ["Fraunces", "Times New Roman", "serif"],
        body: ["Sora", "Trebuchet MS", "sans-serif"],
      },
    },
  },
  plugins: [require("daisyui")],
  daisyui: {
    themes: [
      {
        spooklight: {
          primary: "#F97316",
          "primary-content": "#1E1308",
          secondary: "#0F766E",
          "secondary-content": "#ECFEFF",
          accent: "#E11D48",
          "accent-content": "#FFF1F2",
          neutral: "#1F2937",
          "neutral-content": "#F9FAFB",
          "base-100": "#FFF7ED",
          "base-200": "#FCEAD1",
          "base-300": "#F6D7B3",
          "base-content": "#2A1A12",
          info: "#0EA5E9",
          "info-content": "#E0F2FE",
          success: "#22C55E",
          "success-content": "#ECFDF5",
          warning: "#F59E0B",
          "warning-content": "#3B1D00",
          error: "#EF4444",
          "error-content": "#FFF1F2",
          "--rounded-box": "1.5rem",
          "--rounded-btn": "9999px",
          "--rounded-badge": "1rem",
          "--animation-btn": "0.2s",
          "--animation-input": "0.2s",
          "--btn-focus-scale": "0.98",
          "--border-btn": "1px",
          "--tab-border": "1px",
          "--tab-radius": "0.75rem",
        },
      },
    ],
  },
};
