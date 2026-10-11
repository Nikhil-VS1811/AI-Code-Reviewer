import react from "@vitejs/plugin-react";
import { defineConfig, type PluginOption } from "vite";
import { reticle } from "@reticlehq/vite-plugin";

/**
 * The @reticlehq/vite-plugin package declares a structural Vite plugin interface
 * written against Vite 4/5 types, where `config(config)` expects `server.watch` without
 * Vite 6's `null` union in `ServerOptions.watch` (`WatchOptions | null | undefined`).
 * We explicitly type the adapted instance as Vite's standard `PluginOption` to bridge
 * the Vite 6 type definition gap while keeping strict type checking enabled across the project.
 */
const reticlePlugin: PluginOption = reticle({ captureNetworkBodies: true }) as unknown as PluginOption;

export default defineConfig({
  plugins: [reticlePlugin, react()],
  server: {
    port: 5173,
  },
});
