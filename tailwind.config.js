module.exports = {
  content: ["./src/**/templates/**/*.html", "./src/**/*.py"],
  theme: {
    extend: {
      fontFamily: {
        display: ["Cinzel", "Times New Roman", "serif"],
        body: ["Sora", "Trebuchet MS", "sans-serif"],
      },
    },
  },
  plugins: [require("daisyui")],
  daisyui: {
    themes: [
      {
        spooklight: {
          primary: "#8FB6FF",
          "primary-content": "#0B1021",
          secondary: "#63C6C9",
          "secondary-content": "#062027",
          accent: "#FFC987",
          "accent-content": "#3A2100",
          neutral: "#121A34",
          "neutral-content": "#E6EDFF",
          "base-100": "#0B1021",
          "base-200": "#111C35",
          "base-300": "#172544",
          "base-content": "#E6EDFF",
          info: "#5B9DFF",
          "info-content": "#08162D",
          success: "#43D69E",
          "success-content": "#042017",
          warning: "#F6C177",
          "warning-content": "#3A2100",
          error: "#FCA5A5",
          "error-content": "#2A0B0B",
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
