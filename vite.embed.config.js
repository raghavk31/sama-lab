import { resolve } from "node:path";
import { defineConfig } from "vite";

// The ABM essay as one script + one stylesheet with stable names, for another site to load
// (raghavkohli.xyz copies them with scripts/sync-sama-lab.py). Results are fetched from the URL
// the host gives, so the 130 KB JSON is not inlined into the script.
export default defineConfig({
  publicDir: false,
  build: {
    outDir: "dist/embed",
    emptyOutDir: false,
    copyPublicDir: false,
    minify: true,
    rolldownOptions: { output: { minify: true } },   // lib mode keeps whitespace otherwise
    lib: {
      entry: resolve(import.meta.dirname, "abm/src/embed.js"),
      formats: ["es"],
      fileName: () => "sama-abm.js",
      cssFileName: "sama-abm",
    },
  },
});
