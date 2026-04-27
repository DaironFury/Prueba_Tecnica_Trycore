import path from "node:path";

import react from "@vitejs/plugin-react";
import { defineConfig, loadEnv } from "vite";

/**
 * The frontend always issues requests to relative paths under `/api/`.
 *
 * - In development, Vite proxies `/api` to the URL declared in
 *   `VITE_API_PROXY_TARGET` (defaults to the local backend on port 8000).
 * - In production, nginx serves the static build and proxies `/api` to
 *   the backend service inside the Docker network.
 *
 * Application code never needs to know whether it is running in dev or prod.
 */
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const apiTarget = env.VITE_API_PROXY_TARGET ?? "http://localhost:8000";

  return {
    plugins: [react()],
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "./src"),
      },
    },
    server: {
      host: "0.0.0.0",
      port: 5173,
      proxy: {
        "/api": {
          target: apiTarget,
          changeOrigin: true,
        },
      },
    },
    build: {
      outDir: "dist",
      sourcemap: false,
    },
  };
});
