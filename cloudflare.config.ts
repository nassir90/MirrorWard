import { bindings, defineConfig, triggers } from "cf/config";

export default defineConfig({
  worker: {
    name: "mirror-ward",
    compatibilityDate: "2026-09-25",
    entrypoint: "./worker.js",
    assets: { runWorkerFirst: true },
    env: { ASSETS: bindings.assets() },
    triggers: [triggers.fetch({ pattern: "mpts.ie/games/mirrorward*", zone: "mpts.ie" })],
    observability: { enabled: true },
  },
});
