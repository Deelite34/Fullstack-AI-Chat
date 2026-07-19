import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    cors: false,
    proxy: {
      "/stream": {
        target: "http://backend:8000/",
        changeOrigin: false,
      },
      "/api": {
        target: "http://backend:8000/",
        changeOrigin: false,
      },
    },
  },
});
