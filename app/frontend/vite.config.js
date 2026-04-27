import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  envPrefix: ["VITE_", "API_"],
  build: {
    outDir: "dist",
    assetsDir: "static",
  },
});
