export default {
  darkMode: "class",
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        "primary": "#059669",
        "on-primary": "#ffffff",
        "secondary": "#d97706",
        "on-secondary": "#ffffff",
        "secondary-container": "#f59e0b",
        "on-secondary-container": "#fffbeb",
        "background": "#f8fafc",
        "on-background": "#0f172a",
        "surface": "#ffffff",
        "on-surface": "#0f172a",
        "surface-variant": "#e2e8f0",
        "surface-variant-alt": "#e2e8f0",
        "on-surface-variant": "#475569",
        "surface-container-lowest": "#ffffff",
        "surface-container-low": "#f1f5f9",
        "surface-container-highest": "#cbd5e1",
        "outline": "#94a3b8",
        "outline-variant": "#cbd5e1",
        "error": "#dc2626",
        "on-error": "#ffffff",
        "error-container": "#fef2f2",
        "on-error-container": "#7f1d1d"
      },
      borderRadius: {
        "DEFAULT": "0.25rem",
        "lg": "0.5rem",
        "xl": "0.75rem",
        "2xl": "1rem",
        "3xl": "1.5rem",
        "full": "9999px"
      },
      spacing: {
        "lg": "24px",
        "sm": "8px",
        "margin-desktop": "40px",
        "2xl": "48px",
        "md": "16px",
        "gutter": "16px",
        "base": "4px",
        "margin-mobile": "16px",
        "xs": "4px",
        "xl": "32px",
        "stack-xs": "8px",
        "stack-sm": "12px",
        "stack-md": "16px",
        "stack-lg": "24px",
        "stack-xl": "32px",
        "container-max": "1440px"
      },
      fontFamily: {
        "headline-sm": ["Inter"],
        "headline-md": ["Inter"],
        "body-lg": ["Inter"],
        "body-md": ["Inter"],
        "label-md": ["Inter"],
        "caption": ["Inter"],
        "label-sm": ["Inter"],
        "headline-lg": ["Inter"],
        "headline-lg-mobile": ["Inter"],
        "display-xl": ["Inter"]
      },
      fontSize: {
        "headline-sm": ["20px", {"lineHeight": "28px", "fontWeight": "600"}],
        "headline-md": ["24px", {"lineHeight": "32px", "letterSpacing": "-0.01em", "fontWeight": "600"}],
        "headline-md-mobile": ["22px", {"lineHeight": "30px", "letterSpacing": "-0.01em", "fontWeight": "700"}],
        "body-lg": ["18px", {"lineHeight": "28px", "fontWeight": "400"}],
        "body-md": ["16px", {"lineHeight": "24px", "fontWeight": "400"}],
        "label-md": ["14px", {"lineHeight": "20px", "letterSpacing": "0.01em", "fontWeight": "600"}],
        "caption": ["12px", {"lineHeight": "16px", "fontWeight": "400"}],
        "label-sm": ["12px", {"lineHeight": "16px", "fontWeight": "500"}],
        "headline-lg": ["32px", {"lineHeight": "40px", "letterSpacing": "-0.02em", "fontWeight": "700"}],
        "headline-lg-mobile": ["26px", {"lineHeight": "32px", "letterSpacing": "-0.02em", "fontWeight": "700"}],
        "display-xl": ["48px", {"lineHeight": "56px", "letterSpacing": "-0.02em", "fontWeight": "700"}]
      }
    }
  },
  plugins: [],
}
