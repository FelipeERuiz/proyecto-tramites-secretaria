import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";
import "vuetify/styles";
import "@mdi/font/css/materialdesignicons.css";

export default createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: "light",
    themes: {
      light: {
        colors: {
          primary: "#1565C0",
          secondary: "#37474F",
          accent: "#FF6F00",
          success: "#2E7D32",
          warning: "#F57F17",
          error: "#C62828",
          info: "#0277BD",
        },
      },
    },
  },
  defaults: {
    VBtn: { rounded: "lg", variant: "flat" },
    VCard: { rounded: "lg", elevation: 2 },
    VTextField: { variant: "outlined", density: "comfortable" },
    VSelect: { variant: "outlined", density: "comfortable" },
    VTextarea: { variant: "outlined", density: "comfortable" },
  },
});
