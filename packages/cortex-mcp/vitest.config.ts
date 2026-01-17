import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    environment: "node",
    include: ["tests/**/*.test.ts"],
    exclude: ["tests/cli-integration.test.ts"],
    deps: {
      inline: ["execa"],
    },
  },
});
