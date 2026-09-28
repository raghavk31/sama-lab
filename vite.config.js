import { resolve } from "node:path";
import { defineConfig } from "vite";

// Relative base: the built pages work at raghavk31.github.io/sama-lab/, copied into another static
// site, or inside an iframe, without rebuilding.
export default defineConfig({
  base: "./",
  build: {
    outDir: "dist",
    rollupOptions: {
      input: {
        index: resolve(import.meta.dirname, "index.html"),
        abm: resolve(import.meta.dirname, "abm/index.html"),
      },
    },
  },
});
